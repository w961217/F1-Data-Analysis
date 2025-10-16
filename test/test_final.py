import fastf1
import pandas as pd
from fastf1.events import get_event_schedule
from pathlib import Path

# --- CONFIG ---
YEARS = [2021, 2022, 2023, 2024]
OUTPUT_FILE = Path("csv") / "f1_lap_data_2021_2024_condition_3.0.csv"

all_data = []

for year in YEARS:
    try:
        schedule = get_event_schedule(year)
    except Exception as e:
        print(f"Could not load schedule for {year}: {e}")
        continue

    for _, race in schedule.iterrows():
        gp_name = race['EventName']
        gp_round = race['RoundNumber']

        print(f"Processing {year} {gp_name} (Round {gp_round})...")

        try:
            # --- Load session with lap + weather data ---
            session = fastf1.get_session(year, gp_round, 'R')
            session.load(laps=True, telemetry=False, weather=True)

            if session.laps.empty:
                print(f"No lap data for {year} {gp_name}")
                continue

            # --- Apply strict lap filtering (match degradation script style) ---
            laps_cleaned = session.laps.loc[
                (session.laps['IsAccurate'] == True) &
                (session.laps['LapTime'].notna()) &
                (session.laps['PitOutTime'].isna()) &
                (session.laps['PitInTime'].isna()) &
                (session.laps['TrackStatus'] == '1')
            ].copy()

            if laps_cleaned.empty:
                print(f"No clean laps for {year} {gp_name}")
                continue

            # --- Add LapTimeSeconds like original code ---
            laps_cleaned['LapTimeSeconds'] = laps_cleaned['LapTime'].dt.total_seconds()

            # --- Classification (driver finishing status) ---
            driver_status = {}
            if session.results is not None:
                for _, row in session.results.iterrows():
                    driver_status[row.Abbreviation] = row.Status

            # --- Track status messages (flags) ---
            try:
                track_status = session.track_status
            except Exception:
                track_status = None

            # --- Weather data ---
            weather_data = session.weather_data if not session.weather_data.empty else None

            # --- Iterate over laps ---
            for _, lap in laps_cleaned.iterrows():
                driver = lap['Driver']

                # Flag condition lookup (closest status at lap start)
                flag_status = "Unknown"
                if track_status is not None:
                    ts = track_status.loc[track_status['Time'] <= lap['LapStartTime']]
                    if not ts.empty:
                        last_flag = ts.iloc[-1]['Message']
                        if "Yellow" in last_flag:
                            flag_status = "Yellow"
                        elif "Red" in last_flag:
                            flag_status = "Red"
                        elif "Clear" in last_flag or "Green" in last_flag:
                            flag_status = "Green"

                # Weather lookup (nearest timestamp to lap start)
                track_temp = None
                air_temp = None
                if weather_data is not None:
                    idx = (weather_data['Time'] - lap['LapStartTime']).abs().idxmin()
                    weather_row = weather_data.loc[idx]
                    track_temp = weather_row['TrackTemp']
                    air_temp = weather_row['AirTemp']

                # Append row of structured data
                all_data.append({
                    "Year": year,
                    "GrandPrix": gp_name,
                    "Round": gp_round,
                    "Driver": driver,
                    "LapNumber": lap['LapNumber'],
                    "LapTimeSeconds": lap['LapTimeSeconds'],
                    "Compound": lap['Compound'],
                    "TyreLife": lap['TyreLife'],
                    "TrackTemp": track_temp,
                    "AirTemp": air_temp,
                    "Flag": flag_status,
                    "Status": driver_status.get(driver, "Unknown")
                })

        except Exception as e:
            print(f"Failed to process {year} {gp_name}: {e}")
            continue

# --- Final Export ---
df = pd.DataFrame(all_data)

if not df.empty:
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Data collection complete → {OUTPUT_FILE} ({len(df)} rows)")
else:
    print("No data collected. Check FastF1 cache and API availability.")
