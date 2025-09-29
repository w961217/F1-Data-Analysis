import fastf1
import pandas as pd

# Enable cache (optional, but recommended)
# fastf1.Cache.enable_cache("fastf1_cache")

YEAR = 2023
ROUND = 1   # Bahrain GP as test

session = fastf1.get_session(YEAR, ROUND, 'R')
session.load(laps=True, telemetry=False, weather=True)

if session.laps.empty:
    raise RuntimeError("No lap data available for this session.")

# Try to access track status (flags)
try:
    track_status = session.track_status
except Exception:
    track_status = None

flags = []
for _, lap in session.laps.iterrows():
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
    flags.append(flag_status)

df_flags = pd.DataFrame({"Flag": flags})
summary = df_flags["Flag"].value_counts()

print("Flag counts in race:")
print(summary)

if "Yellow" in summary.index:
    print("Yellow flag data exists")
else:
    print("No Yellow flag data found")

if "Red" in summary.index:
    print("Red flag data exists")
else:
    print("No Red flag data found")

if "Green" in summary.index:
    print("Green flag data exists")
else:
    print("No Green flag data found")
