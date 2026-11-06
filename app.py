import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="VitalClusters", layout="wide")

FEATURES = {
    "stunted": "Child stunting",
    "not_vaccinated_measles": "Children missing measles vaccine",
    "poorest_40pct": "Households in poorest 40%",
    "rural": "Rural population",
    "mother_no_education": "Mothers with no education",
}
SYMPTOMS = {"diarrhea": "Diarrhea", "fever": "Fever", "cough": "Cough"}
feats = list(FEATURES)


@st.cache_data
def load():
    df = pd.read_csv("county_clusters.csv")
    profile = pd.read_csv("cluster_profiles.csv", index_col=0)
    ks = pd.read_csv("k_selection.csv")
    return df, profile, ks


df, profile, ks = load()
df["county_name"] = df["county"].str.title()
k = df["cluster"].nunique()


def cluster_name(c):
    if c == 0:
        tag = "lowest overall risk"
    elif c == k - 1:
        tag = "highest overall risk"
    else:
        tag = "in between"
    return f"Profile {c + 1}: {tag}"


names = {c: cluster_name(c) for c in sorted(df["cluster"].unique())}
df["profile"] = df["cluster"].map(names)
national = df[feats + list(SYMPTOMS)].mean()

st.title("VitalClusters")
st.write(
    "Kenya's 47 counties grouped by child health risk, using the 2022 "
    "Demographic and Health Survey (children under 5). The groups show "
    "patterns, not causes."
)

row = ks[ks["k"] == k].iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Groups", k)
c2.metric("Stability", f"{row['stability']:.2f}",
          help="How often the same groups come back when we re-run on random subsets of counties. 1.0 is perfect.")
c3.metric("Separation", f"{row['silhouette']:.2f}",
          help="Silhouette score. Above 0.5 is strong, 0.25 or below is weak.")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Groups", "Counties", "Method"])

with tab1:
    left, right = st.columns([3, 2])

    with left:
        st.subheader("How the groups differ")
        st.caption("Red is above the average county, blue is below. Higher is worse in every row.")
        heat = profile[feats].copy()
        heat.index = [names[c] for c in heat.index]
        heat.columns = [FEATURES[f] for f in heat.columns]
        fig = px.imshow(heat.round(2), color_continuous_scale="RdBu_r",
                        zmin=-2, zmax=2, aspect="auto", text_auto=True)
        fig.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Counties per group")
        counts = df["profile"].value_counts().reindex([names[c] for c in sorted(names)])
        fig = px.bar(counts, orientation="h", labels={"value": "Counties", "index": ""})
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Map of similarity")
    st.caption("Counties that sit close together have similar profiles.")
    Z = StandardScaler().fit_transform(df[feats].fillna(df[feats].median()))
    pca = PCA(n_components=2, random_state=0)
    pts = pca.fit_transform(Z)
    df["x"], df["y"] = pts[:, 0], pts[:, 1]
    hover = {f: ":.1f" for f in feats}
    hover.update({"x": False, "y": False, "profile": False})
    fig = px.scatter(
        df, x="x", y="y", color="profile", hover_name="county_name",
        hover_data=hover,
        category_orders={"profile": [names[c] for c in sorted(names)]},
        labels={"x": "", "y": ""},
    )
    fig.update_traces(marker=dict(size=11))
    fig.update_layout(legend_title_text="", margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"The two axes keep {pca.explained_variance_ratio_.sum() * 100:.0f}% of the variation in the five indicators.")

with tab2:
    choice = st.selectbox("Group", [names[c] for c in sorted(names)], index=k - 1)
    c = [key for key, v in names.items() if v == choice][0]
    sub = df[df["cluster"] == c]

    st.subheader(choice)
    st.write(f"Stands out for: {sub['cluster_description'].iloc[0]}.")
    st.write(f"{len(sub)} counties: " + ", ".join(sub["county_name"]))

    st.write("Group average, and how far it is from the average county")
    cols = st.columns(len(feats))
    for col, f in zip(cols, feats):
        val, nat = sub[f].mean(), national[f]
        col.metric(FEATURES[f], f"{val:.0f}%", f"{val - nat:+.0f} pts",
                   delta_color="inverse")

    st.write("Recent illness (not used to form the groups)")
    cols = st.columns(len(SYMPTOMS))
    for col, s in zip(cols, SYMPTOMS):
        val, nat = sub[s].mean(), national[s]
        col.metric(SYMPTOMS[s], f"{val:.0f}%", f"{val - nat:+.0f} pts",
                   delta_color="off")
    st.caption("Illness is based on two-week recall in small samples, so it is noisy. Shown for context only.")

with tab3:
    county = st.selectbox("County", sorted(df["county_name"]))
    r = df[df["county_name"] == county].iloc[0]
    st.subheader(f"{county}: {r['profile']}")
    st.write(f"Group pattern: {r['cluster_description']}.")

    cols = st.columns(len(feats))
    for col, f in zip(cols, feats):
        col.metric(FEATURES[f], f"{r[f]:.0f}%", f"{r[f] - national[f]:+.0f} pts",
                   delta_color="inverse")
    st.caption("Change shown against the average county.")

    if r["borderline"]:
        st.warning("This county sits near the edge between two groups.")
    if r["thin_data"]:
        st.warning("Some figures for this county come from fewer than 100 children, so treat them as rough.")
    st.info("A county can differ from its group on individual indicators.")

with tab4:
    st.markdown(
        f"""
**Data.** Kenya DHS 2022, Children's Recode (children under 5). The raw survey
files are not included. They can be downloaded from the DHS Program after
registering. This dashboard only uses county-level summaries.

**Indicators.** Survey-weighted percentages per county for stunting, missing the
measles vaccine (ages 12 to 36 months), households in the poorest 40%, rural
residence and mothers with no education.

**Grouping.** The five indicators are standardized and grouped with K-Means.
Group counts from 3 to 6 were compared on separation, stability across random
subsets of counties and Davies-Bouldin score, and no group could have fewer
than 5 counties. The result is {k} groups.

**Limits.**
- Groups describe patterns, not causes.
- Only children under 5 are covered.
- With 47 counties, small differences between neighbours do not mean much.
- Some counties have small samples. These are flagged in the county view.
- Illness rates are noisy and not used for grouping.
"""
    )
    st.dataframe(ks.round(3), hide_index=True)