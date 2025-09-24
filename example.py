import fastf1 
import pandas as pd 
from matplotlib import pyplot as plt 
import os 

schedule = fastf1.get_event_schedule(2024, include_testing=False)

track_temp = []

for _, event in schedule.iterrows(): 
    try: 
        session = fastf1.get_session(2024, event['RoundNumber'], 'R')
        session.load(weather=True, telemetry=False, laps=False)
        
        weather = session.weather_data 
        avg_track = weather['TrackTemp'].mean()
        avg_air = weather['AirTemp'].mean()
        
        track_temp.append({
            'Round': event['RoundNumber'],
            'Race': event['EventName'],
            'Track Temp (°C)': avg_track,
            'Air Temp (°C)': avg_air
        })
    except Exception as e:
        print(f"Failed {event['EventName']}: {e}")

# Build DataFrame
df = pd.DataFrame(track_temp).sort_values('Round')
print(df)

csv_file = "track_temps_2024.csv"
df.to_csv(csv_file, index=False)
print(f"Saved file")

# Plot
plt.figure(figsize=(12,6))
plt.plot(df['Race'], df['Track Temp (°C)'], marker='o', label='Track Temp')
plt.plot(df['Race'], df['Air Temp (°C)'], marker='s', label='Air Temp')
plt.xticks(rotation=45, ha='right')
plt.ylabel('°C')
plt.title('Average Track & Air Temperatures - F1 2025 Races')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()