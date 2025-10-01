import fastf1
import pandas as pd
from fastf1.events import get_event_schedule
from pathlib import Path

# --- CONFIG ---
YEARS = [2021, 2022, 2023, 2024]
OUTPUT_FILE = Path("csv") / "f1_lap_data_2021_2024_full.csv"

all_data = []

for year in YEARS:
    try:
        schedule = get_event_schedule(year, backend="ergast")
    except Exception as e:
        print(f"Could not load schedule for {year}: {e}")
        continue

    for _, race in schedule.iterrows():
        gp_name = race["EventName"]
        gp_round = race["RoundNumber"]

        print(f"Processing {year} {gp_name} (Round {gp_round})...")

        try:
            # Load session with laps and weather
            session = fastf1.get_session(year, gp_round, "R")
            session.load(laps=True, telemetry=False, weather=True)

            if session.laps.empty:
                print(f"No lap data for {year} {gp_name}")
                continue

            # Prepare weather data: only Time, TrackTemp, AirTemp
            weather = session.weather_data[["Time", "TrackTemp", "AirTemp"]].sort_values("Time")

            # Iterate over all drivers
            for drv in session.drivers:
                drv_laps = session.laps.pick_drivers(drv).sort_values("Time").copy()

                # Merge nearest weather sample for each lap
                drv_laps = pd.merge_asof(
                    drv_laps, weather, on="Time", direction="nearest"
                )

                # Append all laps (no filtering)
                for _, lap in drv_laps.iterrows():
                    all_data.append({
                        "Year": year,
                        "GrandPrix": gp_name,
                        "Round": gp_round,
                        "Driver": lap["Driver"],
                        "LapNumber": lap["LapNumber"],
                        "LapTimeSeconds": lap["LapTime"].total_seconds() if pd.notnull(lap["LapTime"]) else None,
                        "Compound": lap["Compound"],
                        "TyreLife": lap["TyreLife"],
                        "TrackTemp": lap["TrackTemp"],
                        "AirTemp": lap["AirTemp"],
                    })

        except Exception as e:
            print(f"Failed to process {year} {gp_name}: {e}")
            continue

# --- Export to CSV ---
df = pd.DataFrame(all_data)

if not df.empty:
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Data collection complete. Saved to {OUTPUT_FILE} ({len(df)} rows)")
else:
    print("No data collected. Check FastF1 cache and API availability.")
