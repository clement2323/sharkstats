import pandas as pd
from pathlib import Path
import numpy as np
import calendar

data_dir = Path("../data")

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

df.to_csv(data_dir / "data_clean.csv")
