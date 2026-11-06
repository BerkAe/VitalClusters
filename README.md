# VitalClusters

Survey data on child health usually comes as huge tables that only a specialist can read. I wanted to see if anyone could look at the same data and quickly understand which counties are struggling.

VitalClusters takes Kenya's 2022 Demographic and Health Survey, turns it into county-level numbers, groups the 47 counties into a few health risk profiles and shows the result in a small dashboard that explains each group in simple language.

I built it for DHS Hacks V2.

## What it does

- Cleans the survey data and works out weighted rates for each county (stunting, missing the measles vaccine, poverty, rural residence, mothers with no education)
- Tries 3 to 6 groups and picks the number automatically
- Checks how stable the groups are by re-running the clustering on random subsets of counties
- Describes each group shortly and shows how it differs from the average county
- Marks counties that sit near the edge of a group

## What I found

The data splits into 3 groups. They were stable (0.96 on the stability check) and moderately separated (silhouette 0.40):

1. **Lower overall risk (13 counties):** less rural and wealthier, like Nairobi, Kiambu, Mombasa and Nakuru.
2. **In between (26 counties):** mostly rural, with better maternal education and vaccination.
3. **Higher overall risk (8 counties):** mostly in the north, such as Mandera, Wajir, Turkana and West Pokot, with more poverty, more mothers with no education and more children missing the measles vaccine.

These groups describe patterns, not causes. The third group is mainly defined by education, vaccination and poverty, and its stunting rate isn't much higher than the middle group's. The groups also don't match every indicator: Kilifi has the highest stunting rate in the country but sits in the middle group. That's why the dashboard also shows each county's own numbers.

## Run it yourself

Tested on Python 3.14.

```
pip install -r requirements.txt
```

The raw survey data isn't in this repo, because DHS data can't be redistributed. To get it, register at [dhsprogram.com](https://dhsprogram.com), request access, and download the Kenya 2022 Children's Recode in Stata format (`KEKR8CDT.ZIP`). Unzip it and put the `.DTA` file in a folder called `data/`.

Then run these from the project folder:

```
python src/aggregate.py
python src/cluster.py
streamlit run app.py
```

The first script builds `county_indicators.csv`, the second makes the groups and writes the three files the dashboard reads. The CSVs are already in this repo, so if you just want to look at the dashboard you can skip straight to `streamlit run app.py`.

Note: the dashboard has to be started with `streamlit run app.py`. Running `python app.py` will only print warnings.

## Files

- `src/aggregate.py` turns the survey into one row per county
- `src/cluster.py` chooses the number of groups, clusters, and writes the descriptions
- `app.py` is the Streamlit dashboard
- `county_*.csv`, `cluster_profiles.csv` and `k_selection.csv` are county-level results only, with no individual survey records

## Limits

- It only covers children under 5, so these are child health profiles, not whole-population ones
- Measles vaccination is only recorded up to about 36 months, so that rate covers children aged 12 to 36 months
- With 47 counties, small differences between neighbouring counties don't mean much
- Some counties have small samples for certain indicators, and the dashboard warns you about those
- Recent illness (diarrhea, fever, cough) comes from a two-week recall in small samples and is very noisy. The dashboard shows it, but I left it out of the clustering
- Everything here is based on a single survey year

## What I'd do next

- Add more countries and survey years
- Track how groups change over time to spot new problem areas early
- Show uncertainty for every county, not just the borderline cases

## Data and license

Survey data: Kenya DHS 2022, The DHS Program. Code is under the MIT license.
