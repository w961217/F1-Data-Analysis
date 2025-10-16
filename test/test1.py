import fastf1
from fastf1.events import get_event_schedule 
import pandas as pd

# Enable FastF1 cache (default location is ~/.fastf1)
# fastf1.Cache.enable_cache("fastf1_cache")

YEARS = [2021, 2022, 2023, 2024]
OUTPUT_FILE = "f1_lap_data_2021_2024.csv"

all_data = []

for year in YEARS:
    try:
        schedule = get_event_schedule(year, force_ergast=True)  # safer
    except Exception as e:
        print(f"Could not load schedule for {year}: {e}")
        continue

    for _, race in schedule.iterrows():
        gp_name = race['EventName']
        gp_round = race['RoundNumber']

        print(f"\n➡ Processing {year} {gp_name} (Round {gp_round})...")

        try:
            session = fastf1.get_session(year, gp_round, 'R')  # Race session
            # Force loading laps + weather
            session.load(laps=True, telemetry=False, weather=True)

            if session.laps.empty:
                print(f"No lap data available for {year} {gp_name}")
                continue

            for drv in session.drivers:
                drv_laps = session.laps.pick_drivers(drv)
                for _, lap in drv_laps.iterrows():
                    all_data.append({
                        "Year": year,
                        "GrandPrix": gp_name,
                        "Round": gp_round,
                        "Driver": lap['Driver'],
                        "LapNumber": lap['LapNumber'],
                        "LapTime": lap['LapTime'].total_seconds() if pd.notnull(lap['LapTime']) else None,
                        "Compound": lap['Compound'],
                        "TyreLife": lap['TyreLife'],
                        "TrackTemp": lap.get('TrackTemp', None)  # use .get to avoid crash if missing
                    })

        except Exception as e:
            print(f"❌ Failed to process {year} {gp_name}: {e}")
            continue

df = pd.DataFrame(all_data)

if not df.empty:
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Data collection complete. Saved to {OUTPUT_FILE} with {len(df)} rows")
else:
    print("No data collected. Check FastF1 cache and API availability.")
