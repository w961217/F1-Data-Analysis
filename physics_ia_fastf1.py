import fastf1
from fastf1.events import get_event_schedule
import pandas as pd
from pathlib import Path

YEARS = [2022, 2023, 2024]
OUTPUT = Path("csv") / "fastf1_lap_data1.csv"

all_data = []

for year in YEARS:
    try:
        schedule = get_event_schedule(year)
    except Exception as e:
        print(f"Could not load schedule for {year}: {e}")
        continue
    for _, race in schedule.iterrows():
        gp = race["EventName"]
        gp_round = race["RoundNumber"]
        print(f"Processing {year} {gp} (Round {gp_round})...")

        try:
            # Load session
            session = fastf1.get_session(year, gp_round, "R")
            session.load(laps=True, telemetry=False, weather=True)

            if session.laps.empty:
                print(f"No lap data available for {year} {gp}")
                continue
            # Clean laps filter
            laps_cleaned = session.laps.loc[
                (session.laps["IsAccurate"] == True)
                & (session.laps["LapTime"].notna())
                & (session.laps["PitOutTime"].isna())
                & (session.laps["PitInTime"].isna())
                & (session.laps["TrackStatus"] == "1")
            ].copy()

            if laps_cleaned.empty:
                print(f"No clean laps available for {year} {gp}")
                continue
            # Laptime in seconds
            laps_cleaned["LapTimeSeconds"] = laps_cleaned["LapTime"].dt.total_seconds()
            # Driver status
            driver_status = {}
            if session.results is not None:
                for _, row in session.results.iterrows():
                    driver_status[row.Abbreviation] = row.Status
            # Track condition
            try:
                track_status = session.track_status
            except Exception:
                track_status = None
            # Weather data
            weather_data = (
                session.weather_data if not session.weather_data.empty else None
            )

            for _, lap in laps_cleaned.iterrows():
                driver = lap["Driver"]

                flag_status = "Unknown"
                if track_status is not None:
                    ts = track_status[track_status["Time"] <= lap["LapStartTime"]]
                    if not ts.empty:
                        last_flag = ts.iloc[-1]["Message"]
                        if "Yellow" in last_flag:
                            flag_status = "Yellow"
                        elif "Red" in last_flag:
                            flag_status = "Red"
                        elif "Clear" in last_flag or "Green" in last_flag:
                            flag_status = "Green"

                track_temp, air_temp = None, None
                if weather_data is not None and not weather_data.empty:
                    idx = (weather_data["Time"] - lap["LapStartTime"]).abs().idxmin()
                    weather_row = weather_data.loc[idx]
                    track_temp = weather_row["TrackTemp"]
                    air_temp = weather_row["AirTemp"]

                all_data.append(
                    {
                        "Year": year,
                        "GrandPrix": gp,
                        "Round": gp_round,
                        "Driver": driver,
                        "DriverNumber": lap["DriverNumber"],
                        "Stint": lap["Stint"],
                        "LapNumber": lap["LapNumber"],
                        "LapTime": lap["LapTimeSeconds"],
                        "Compound": lap["Compound"],
                        "TyreLife": lap["TyreLife"],
                        "TrackTemp": track_temp,
                        "AirTemp": air_temp,
                        "Flag": flag_status,
                        "Status": driver_status.get(driver, "Unknown"),
                    }
                )

        except Exception as e:
            print(f"Failed to process {year} {gp}: {e}")
            continue

df = pd.DataFrame(all_data)

if not df.empty:
    df.to_csv(OUTPUT, index=False)
    print(f"Saved to {OUTPUT}")
else:
    print("No data collected.")
