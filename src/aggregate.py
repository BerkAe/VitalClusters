import numpy as np
import pandas as pd

path = "data/KEKR8CFL.DTA"
cols = ["v024", "v005", "b5", "hw1", "hw70", "h9", "h11", "h22", "h31",
        "v106", "v190", "v025"]

df = pd.read_stata(path, convert_categoricals=False, columns=cols)
labels = pd.read_stata(path, convert_categoricals=True, columns=["v024"])["v024"]
df["county"] = labels.astype(str).str.strip()
df["w"] = df["v005"] / 1_000_000

alive = df["b5"] == 1


def flag(condition, valid):
    out = pd.Series(np.nan, index=df.index)
    out[valid] = condition[valid].astype(float)
    return out


ind = pd.DataFrame({"county": df["county"], "w": df["w"]})

measured = alive & df["hw70"].between(-600, 600)
ind["stunted"] = flag(df["hw70"] < -200, measured)

eligible = alive & df["hw1"].between(12, 59) & df["h9"].isin([0, 1, 2, 3])
ind["not_vaccinated_measles"] = flag(df["h9"] == 0, eligible)

for col, name in [("h11", "diarrhea"), ("h22", "fever"), ("h31", "cough")]:
    answered = alive & df[col].isin([0, 1, 2])
    ind[name] = flag(df[col].isin([1, 2]), answered)

ind["poorest_40pct"] = flag(df["v190"].isin([1, 2]), alive)
ind["rural"] = flag(df["v025"] == 2, alive)
ind["mother_no_education"] = flag(df["v106"] == 0, alive)

indicators = [c for c in ind.columns if c not in ("county", "w")]


def weighted_pct(group, col):
    s = group[[col, "w"]].dropna()
    if s.empty:
        return np.nan
    return np.average(s[col], weights=s["w"]) * 100


rows = []
for county, group in ind.groupby("county"):
    row = {"county": county, "n_children": len(group)}
    for c in indicators:
        row[c] = weighted_pct(group, c)
        row[f"n_{c}"] = group[c].notna().sum()
    rows.append(row)

out = pd.DataFrame(rows).sort_values("county")
out.to_csv("county_indicators.csv", index=False)

print(out[["county", "n_children"] + indicators].round(1).to_string())
print("\nSmallest sample behind each rate:")
print(out[[f"n_{c}" for c in indicators]].min())