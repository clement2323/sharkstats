import pandas as pd
from pathlib import Path
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import calendar

data_dir = Path("data")

df = pd.read_excel(
    data_dir / "Australian Shark-Incident Database Public Version.xlsx",
    sheet_name="ASID",
)

df["Time.of.incident"] = (
    df["Time.of.incident"].astype(str).str.replace(",", "", regex=False).str.zfill(4)
)
df.loc[df["Time.of.incident"] == "0nan", "Time.of.incident"] = np.nan


df["Hour_int"] = pd.to_numeric(df["Time.of.incident"].str[:2], errors="coerce")
df["Minute_int"] = pd.to_numeric(df["Time.of.incident"].str[2:], errors="coerce")

df["Hour_ceil"] = df["Hour_int"] + (df["Minute_int"] > 30).astype(int)
df["Hour_ceil"] = df["Hour_ceil"].clip(upper=24)


# Créer une colonne avec le nom du mois
df["Incident.month.name"] = df["Incident.month"].apply(
    lambda x: calendar.month_name[x] if pd.notna(x) else np.nan
)

counts = df["Hour_ceil"].value_counts().sort_index()

plt.figure(figsize=(10, 6))
plt.bar(counts.index, counts.values, color="skyblue", edgecolor="black")
plt.xticks(range(0, 25), [f"{h}:00" for h in range(25)])
plt.xlabel("Hour of incident (ceiled)")
plt.ylabel("Number of incidents")
plt.title("Incidents by hour (rounded up, NA ignored)")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()
# difficult to interpret is this because several surfers surf during the afternoon or because it is more dangerous to surf during the afternoon ?
# rapport to number of surfers ??

counts_month = (
    df["Incident.month.name"].value_counts().reindex(list(calendar.month_name[1:]))
)  # pour garder l'ordre Jan→Dec

plt.figure(figsize=(10, 6))
plt.bar(counts_month.index, counts_month.values, color="skyblue", edgecolor="black")
plt.xlabel("Month")
plt.ylabel("Number of incidents")
plt.title("Incidents per month")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

# same more accidents in summer.. but affluences ?

# Basic statisticsdf.
df["Incident.month"]
df["State"].value_counts()
df["Incident.year"]

df[["State", "Incident.year"]].value_counts().unstack(fill_value=0)

pivot = pd.pivot_table(
    df, index="State", columns="Incident.year", aggfunc="size", fill_value=0
)

#
pivot = df[["State", "Incident.year"]].value_counts().unstack(fill_value=0)

pivot_smooth = pivot.T.rolling(window=3, min_periods=1).mean()

pivot_smooth.plot()
plt.xlabel("Year")
plt.ylabel("Number of incidents (3-year average)")
plt.title("Incidents per year by State (3-year smoothed)")
plt.grid(True)
plt.show()

# bias : some states are bigger than the others, information quality in former years ?
# n b attacks by inhabitants ? by surfers ?

# same with "fatal injuries"
#
df[df["Victim.injury"] == "fatal"][["State", "Incident.year"]].value_counts().unstack(
    fill_value=0
)


## ok Transformation en geopandas data frame

import geopandas as gpd
from shapely.geometry import Point
import folium

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
    crs="EPSG:4326",  # WGS84 (standard GPS)
)


# Center map on mean coordinates
m = folium.Map(
    location=[
        gdf["Latitude"].astype(float).mean(),
        gdf["Longitude"].astype(float).mean(),
    ],
    zoom_start=5,
)


for _, row in gdf.iterrows():

    color = "red" if row["Victim.injury"] == "fatal" else "blue"

    html = f"""
    <div style="width:250px;">
        <b>State:</b> {row['State']}<br>
        <b>Year:</b> {row['Incident.year']}<br>
        <b>shark type:</b> {row['Shark.common.name']}
    </div>
    """

    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=4,
        popup=folium.Popup(html, max_width=300),
        fill=True,
        fill_color=color,
        color=color,
    ).add_to(m)


output_dir = Path("output")
m.save(output_dir / "map.html")

# gestion du temps sur 4 position 2000 etc..
# faire une heatmap heure jour ??

"Shark.common.name"

## type de shark aussi intéressant croisé avec deadly attack

"Time.of.incident"

# find the polygon of australian states and color them according to the number of attack
# detat
