import fastf1
from fastf1.events import get_event_schedule
import pandas as pd
from pathlib import Path 

YEARS = [2021, 2022, 2023, 2024]
OUTPUT_DIR = Path("csv")
OUTPUT_DIR.mkdir(exist_ok=True)

for year in YEARS:
    all_data = []

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
            session = fastf1.get_session(year, gp_round, 'R')
            session.load(laps=True, telemetry=False, weather=True)

            if session.laps.empty:
                print(f"No lap data available for {year} {gp_name}")
                continue

            # --- Apply same filtering as degradation analysis ---
            laps_cleaned = session.laps.loc[
                (session.laps['IsAccurate'] == True) &
                (session.laps['LapTime'].notna()) &
                (session.laps['PitOutTime'].isna()) &
                (session.laps['PitInTime'].isna()) &
                (session.laps['TrackStatus'] == '1')
            ].copy()

            if laps_cleaned.empty:
                print(f"No clean laps available for {year} {gp_name}")
                continue

            # Race classification → retirements/accidents
            classification = session.results
            driver_status = {}
            if classification is not None:
                for _, row in classification.iterrows():
                    driver_status[row.Abbreviation] = row.Status

            # Track status (flags)
            try:
                track_status = session.track_status
            except Exception:
                track_status = None

            for drv in laps_cleaned['Driver'].unique():
                drv_laps = laps_cleaned.loc[laps_cleaned['Driver'] == drv]
                
                for _, lap in drv_laps.iterrows():
                    # --- Flag condition lookup ---
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

                    # --- Weather lookup using session.weather_data ---
                    track_temp = None
                    air_temp = None
                    if not session.weather_data.empty:
                        idx = (session.weather_data['Time'] - lap['LapStartTime']).abs().idxmin()
                        weather_row = session.weather_data.loc[idx]
                        track_temp = weather_row['TrackTemp']
                        air_temp = weather_row['AirTemp']

                    all_data.append({
                        "Year": year,
                        "GrandPrix": gp_name,
                        "Round": gp_round,
                        "Driver": lap['Driver'],
                        "LapNumber": lap['LapNumber'],
                        "LapTime": lap['LapTime'].total_seconds() if pd.notnull(lap['LapTime']) else None,
                        "Compound": lap['Compound'],
                        "TyreLife": lap['TyreLife'],
                        "TrackTemp": track_temp,
                        "AirTemp": air_temp,
                        "Flag": flag_status,
                        "Status": driver_status.get(lap['Driver'], "Unknown")
                    })

        except Exception as e:
            print(f"Failed to process {year} {gp_name}: {e}")
            continue

    df = pd.DataFrame(all_data)
    if not df.empty:
        output_file = OUTPUT_DIR / f"f1_lap_data_{year}_condition.csv"
        df.to_csv(output_file, index=False)
        print(f"Data for {year} saved to {output_file} with {len(df)} rows")
    else:
        print(f"No data collected for {year}.")
