import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Use default FastF1 cache (no need to set a folder)
# fastf1.Cache.enable_cache()  # optional, default is used automatically

# Years to extract
start_year = 2021
end_year = 2025

# Collect all weather data
all_weather = []

for year in range(start_year, end_year + 1):
    schedule = fastf1.get_event_schedule(year)

    for _, race in schedule.iterrows():
        grand_prix = race["EventName"]
        session_type = "R"  # Race session
        print(f"Processing {grand_prix} {year}...")

        try:
            session = fastf1.get_session(year, grand_prix, session_type)
            session.load()
            weather_data = session.weather_data

            if weather_data.empty:
                print(f"No weather data for {grand_prix} {year}")
                continue

            weather_data["Year"] = year
            weather_data["GrandPrix"] = grand_prix
            weather_data["SessionType"] = session_type
            all_weather.append(weather_data)

        except Exception as e:
            print(f"Failed to process {grand_prix} {year}: {e}")

# Combine all data
if all_weather:
    combined_df = pd.concat(all_weather, ignore_index=True)
    combined_csv = "all_f1_weather_2021_onwards.csv"
    combined_df.to_csv(combined_csv, index=False)
    print(f"All weather data saved to {combined_csv}")

    # --- Plotting with plain Matplotlib ---
    plt.figure(figsize=(16, 8))

    # Create a color map with enough unique colors
    races = combined_df.groupby(["Year", "GrandPrix"]).size().index
    colors = cm.get_cmap("tab20", len(races))  # up to 20 unique colors

    for i, ((year, gp), group) in enumerate(combined_df.groupby(["Year", "GrandPrix"])):
        plt.plot(
            group["Time"],
            group["AirTemp"],
            label=f"{gp} {year} AirTemp",
            color=colors(i),
            linestyle="-",
        )
        plt.plot(
            group["Time"],
            group["TrackTemp"],
            label=f"{gp} {year} TrackTemp",
            color=colors(i),
            linestyle="--",
        )

    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.title("F1 Weather Data (AirTemp & TrackTemp) 2021 Onwards")
    plt.legend(fontsize="small", ncol=2)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

else:
    print("No weather data found.")
