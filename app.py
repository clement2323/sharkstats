import streamlit as st
import pandas as pd
import altair as alt
from streamlit_folium import st_folium
from src.interactive_map import create_interactive_figure
import calendar

# Charger les données
df = pd.read_csv("data/data_clean.csv")

# Configuration de la page
st.set_page_config(
    page_title="Incidents by State Dashboard",
    page_icon=":map:",
    layout="wide",
)

# Titre
st.title("📊 Incidents by State Dashboard")

# --- Sélection des États avec limite à 3 ---
STATES = sorted(df["State"].unique())
selected_states = st.multiselect(
    "Select up to 3 States",
    options=STATES,
    default=STATES[0:2],
    max_selections=4,  # ⚠️ Streamlit 1.27+ supporte max_selections
    help="You can compare up to 4 states at a time",
)

if not selected_states:
    st.warning("Please select at least one state.")
    st.stop()

# --- Sélection de l'année via curseur ---
min_year = int(df["Incident.year"].min())
max_year = int(df["Incident.year"].max())
selected_year = st.slider(
    "Select Year",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1,
)

# Filtrer les données par État et Année
# selected_states = ["WA"]
# selected_year = [1980,2025]
filtered_df = df[
    (df["State"].isin(selected_states))
    & (df["Incident.year"] >= selected_year[0])
    & (df["Incident.year"] <= selected_year[1])
]

if filtered_df.empty:
    st.warning("No data available for the selected states and year range.")
    st.stop()

# --- Créer et centrer la carte Folium sur les incidents filtrés ---
map = create_interactive_figure(filtered_df)

st.subheader("Interactive Map of Australia")

# Centrer la carte avec une colonne vide à gauche et à droite
cols = st.columns([1, 3, 1])
with cols[1]:
    st_folium(map, width=1200, height=600)

# --- Séparation ---
st.divider()

# Section pour les graphiques "peer average"
st.subheader("State vs Peer Average")

NUM_COLS = min(len(selected_states), 3)  # limiter à 3 colonnes
graph_cols = st.columns(NUM_COLS)

for i, state in enumerate(selected_states):
    # state= "WA"
    peers = df
    # --- Graphs par heure ---
    state_data_hour = (
        filtered_df[filtered_df["State"] == state]["Hour_ceil"]
        .value_counts()
        .sort_index()
        .reindex(range(24), fill_value=0)
    )

    peer_avg_hour = (
        peers.groupby("State")["Hour_ceil"]
        .value_counts()
        .unstack(fill_value=0)
        .mean(axis=0)
        .reindex(range(24), fill_value=0)
    )

    # --- Graphs par mois ---
    months = list(calendar.month_name[1:])
    state_data_month = (
        filtered_df[filtered_df["State"] == state]["Incident.month.name"]
        .value_counts()
        .reindex(months, fill_value=0)
    )

    peer_avg_month = (
        peers.groupby("State")["Incident.month.name"]
        .value_counts()
        .unstack(fill_value=0)
        .mean(axis=0)
        .reindex(months, fill_value=0)
    )

    # --- Graphs par année ---
    state_data_year = (
        filtered_df[filtered_df["State"] == state].groupby("Incident.year").size()
    )
    peer_avg_year = (
        peers.groupby("State")["Incident.year"]
        .value_counts()
        .unstack(fill_value=0)
        .mean(axis=0)
    )

    all_years = state_data_year.index.union(peer_avg_year.index)
    state_data_year = state_data_year.reindex(all_years, fill_value=0)
    peer_avg_year = peer_avg_year.reindex(all_years, fill_value=0)

    # --- Préparer les données Altair ---
    plot_data_hour = pd.DataFrame(
        {
            "Hour": state_data_hour.index,
            state: state_data_hour.values,
            "Peer average": peer_avg_hour.values,
        }
    ).melt(id_vars=["Hour"], var_name="Series", value_name="Incidents")

    plot_data_month = pd.DataFrame(
        {
            "Month": state_data_month.index,
            state: state_data_month.values,
            "Peer average": peer_avg_month.values,
        }
    ).melt(id_vars=["Month"], var_name="Series", value_name="Incidents")

    plot_data_month["Month"] = pd.Categorical(
        plot_data_month["Month"], categories=list(calendar.month_name[1:]), ordered=True
    )

    plot_data_year = pd.DataFrame(
        {
            "Year": state_data_year.index,
            state: state_data_year.values,
            "Peer average": peer_avg_year.values,
        }
    ).melt(id_vars=["Year"], var_name="Series", value_name="Incidents")

    # --- Créer les graphiques Altair ---
    color_scale = alt.Scale(
        domain=[state, "Peer average"],
        range=["red", "#87CEFA"],  # dark blue for state, light blue for peer
    )

    chart_hour = (
        alt.Chart(plot_data_hour)
        .mark_line()
        .encode(
            alt.X("Hour:O", title="Hour of the day"),
            alt.Y("Incidents:Q", title="Number of incidents"),
            alt.Color("Series:N", scale=color_scale),
        )
        .properties(title=f"{state} - Incidents by Hour", height=300)
    )

    chart_month = (
        alt.Chart(plot_data_month)
        .mark_line()
        .encode(
            alt.X("Month", title="Month"),
            alt.Y("Incidents:Q", title="Number of incidents"),
            alt.Color("Series:N", scale=color_scale),
        )
        .properties(title=f"{state} - Incidents by Month", height=300)
    )

    chart_year = (
        alt.Chart(plot_data_year)
        .mark_line()
        .encode(
            alt.X("Year:O", title="Year"),
            alt.Y("Incidents:Q", title="Number of incidents"),
            alt.Color("Series:N", scale=color_scale),
        )
        .properties(title=f"{state} - Incidents by Year", height=300)
    )

    with graph_cols[i % NUM_COLS]:
        with st.container():
            st.altair_chart(chart_hour, use_container_width=True)
            st.altair_chart(chart_month, use_container_width=True)
            st.altair_chart(chart_year, use_container_width=True)
