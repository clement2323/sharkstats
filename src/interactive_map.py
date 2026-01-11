import geopandas as gpd
import folium


def create_interactive_figure(df):

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
        crs="EPSG:4326",  # WGS84 (standard GPS)
    )

    # Center map on mean coordinates
    m = folium.Map(
        location=[-25.2744, 133.7751],
        zoom_start=4,
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

    return m
