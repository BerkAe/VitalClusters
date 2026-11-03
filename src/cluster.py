import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler

data = pd.read_csv("county_indicators.csv")

names = {
    "stunted": "child stunting",
    "not_vaccinated_measles": "children missing the measles vaccine",
    "poorest_40pct": "households in the poorest 40%",
    "rural": "rural population",
    "mother_no_education": "mothers with no education",
}
illness = ["diarrhea", "fever", "cough"]
cols = list(names)

X = data[cols].fillna(data[cols].median())
Z = StandardScaler().fit_transform(X)


def stability(Z, k, runs=50):
    rng = np.random.default_rng(0)
    base = KMeans(n_clusters=k, n_init=20, random_state=0).fit(Z)
    scores = []
    for _ in range(runs):
        keep = rng.choice(len(Z), int(0.8 * len(Z)), replace=False)
        part = KMeans(n_clusters=k, n_init=20, random_state=0).fit(Z[keep])
        scores.append(adjusted_rand_score(base.labels_[keep], part.labels_))
    return np.mean(scores)


results = []
for k in range(3, 7):
    model = KMeans(n_clusters=k, n_init=20, random_state=0).fit(Z)
    results.append({
        "k": k,
        "silhouette": silhouette_score(Z, model.labels_),
        "davies_bouldin": davies_bouldin_score(Z, model.labels_),
        "stability": stability(Z, k),
        "min_size": np.bincount(model.labels_).min(),
    })
results = pd.DataFrame(results)
print(results.round(3).to_string(index=False))

valid = results[results["min_size"] >= 5]
if valid.empty:
    valid = results
valid = valid.assign(score=valid["silhouette"].rank()
                     + valid["stability"].rank()
                     + (-valid["davies_bouldin"]).rank())
k = int(valid.sort_values("score").iloc[-1]["k"])
chosen = results[results["k"] == k].iloc[0]
print(f"\nChosen k: {k} (silhouette {chosen['silhouette']:.2f}, stability {chosen['stability']:.2f})")

model = KMeans(n_clusters=k, n_init=20, random_state=0).fit(Z)

scaled = pd.DataFrame(Z, columns=cols)
scaled["raw"] = model.labels_
order = scaled.groupby("raw")[cols].mean().mean(axis=1).sort_values().index
data["cluster"] = scaled["raw"].map({old: new for new, old in enumerate(order)})
scaled["cluster"] = data["cluster"]

d = np.sort(model.transform(Z), axis=1)
data["boundary_ratio"] = d[:, 0] / d[:, 1]
data["borderline"] = data["boundary_ratio"] > 0.85

sample_cols = [f"n_{c}" for c in cols if f"n_{c}" in data.columns]
data["min_sample"] = data[sample_cols].min(axis=1)
data["thin_data"] = data["min_sample"] < 100

profile = scaled.groupby("cluster")[cols].mean()


def describe(c):
    top = profile.loc[c].sort_values(key=abs, ascending=False).index[:3]
    return ", ".join(("higher " if profile.loc[c, f] > 0 else "lower ") + names[f] for f in top)


text = {c: describe(c) for c in profile.index}
data["cluster_description"] = data["cluster"].map(text)

print("\nClusters (0 is lowest overall risk)")
for c in sorted(text):
    group = data[data["cluster"] == c]
    print(f"\nCluster {c}, {len(group)} counties: {text[c]}")
    print("  " + ", ".join(group["county"]))
    print("  Average illness rates: " + ", ".join(f"{s} {group[s].mean():.1f}%" for s in illness))

print("\nBorderline counties:", data.loc[data["borderline"], "county"].tolist())
print("Counties with thin data:", data.loc[data["thin_data"], "county"].tolist())

data.to_csv("county_clusters.csv", index=False)
profile.to_csv("cluster_profiles.csv")
results.to_csv("k_selection.csv", index=False)
print("\nSaved county_clusters.csv, cluster_profiles.csv, k_selection.csv")