# VitalClusters

Survey data on child health usually comes as huge tables that only a specialist can read. I wanted to see if anyone could look at the same data and quickly understand which places are struggling in similar ways.

VitalClusters takes Kenya's 2022 Demographic and Health Survey, turns it into county-level numbers, groups the 47 counties into a few health risk profiles and shows the result in a small dashboard that explains each group in a simple language.

I built it for DHS Hacks V2.

## What it does

- Cleans the survey data and works out weighted rates for each county (stunting, missing the measles vaccine, poverty, rural residence, mothers with no education)
- Tries 3 to 6 groups and picks the best number automatically
- Checks how stable the groups are by re-running the clustering on random subsets of counties
- Shortly describes each group and shows how it differs from the average county
- Flags counties that sit near the edge of a group

## What I found

The data splits into 3 groups, and they were stable (0.96 on the stability check, silhouette 0.40):

1. **Lower overall risk (13 counties):** mostly urban and wealthier, like Nairobi, Kiambu, Mombasa and Nakuru.
2. **In between (26 counties):** mostly rural, with better maternal education and vaccination.
3. **Higher overall risk (8 counties):** mostly in the north, such as Mandera, Wajir, Turkana and West Pokot, with more poverty, more mothers with no education and more children missing the measles vaccine.

These groups describe patterns, not causes. They also don't match every indicator: Kilifi has one of the highest stunting rates but sits in the middle group which is why the dashboard also shows each county's own numbers.

## Run it yourself

You need Python 3.8 or newer.

```
pip install pandas numpy scikit-learn plotly streamlit
```

Raw survey data isn't in this repo because of ethical reasons so you need to register at [dhsprogram.com](https://dhsprogram.com), request access, and download the Kenya 2022 Children's Recode in Stata format (`KEKR8CDT.ZIP`). And put the `.DTA` file in a folder called `data/`.

Then run these from the project folder:

```
python src/aggregate.py
python src/cluster.py
streamlit run app.py
```

The first script builds `county_indicators.csv`, the second makes the groups and writes the three files the dashboard reads. The CSVs are alredy in this repo so you can skip straight to `streamlit run app.py` if you just want to check the dashboard.

## Files

- `src/aggregate.py` turns the survey into one row per county
- `src/cluster.py` chooses the number of groups, clusters, and writes the descriptions
- `app.py` is the Streamlit dashboard
- `county_*.csv`, `cluster_profiles.csv` and `k_selection.csv` are county-level results only, with no individual survey records

## Limits

- It only covers children under 5, so these are child health profiles, not whole-population ones
- With 47 counties, small differences between neighbouring counties don't mean much
- Some counties have small samples for certain indicators, and the dashboard warns you about those
- Recent illness (diarrhea, fever, cough) comes from a two-week recall in small samples and is very noisy. The dashboard shows it, but I left it out of the clustering because it made the groups unstable
- Everything here is based on a single survey year

## What I'd do next

- Add more countries and survey years
- Track how groups change over time to spot new problem areas early
- Show uncertainty for every county, not just the borderline cases

## Data and license

Survey data: Kenya DHS 2022, The DHS Program. Code is under the MIT license.
