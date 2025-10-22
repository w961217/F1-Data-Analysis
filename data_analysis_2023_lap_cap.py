import pandas as pd
from scipy import stats

# Load the data
df = pd.read_csv(r"C:\Users\wesle\Programming\Python\F1-Data-Analysis\csv\fastf1_lap_data.csv")

# Clean and filter the data
df = df.dropna(subset=["TyreLife", "LapTime", "Compound", "TrackTemp"])
df = df[df["LapTime"] > 0]

# Only use 2023 data
df = df[df["Year"] == 2023]

# Filter for SOFT compound only
df = df[df["Compound"] == "SOFT"]

print("Dataset Overview (2023 season, SOFT tyres only):")
print(f"Total laps analyzed: {len(df):,}")
print(f"Grand Prix events: {df['GrandPrix'].nunique()}")
print(f"Drivers: {df['Driver'].nunique()}")
print("\n" + "=" * 80 + "\n")

# Analyze by Grand Prix, Driver, and Stint
print("ANALYSIS BY GRAND PRIX, DRIVER, AND STINT (2023, SOFT tyres, 10–20 laps only):")
print("-" * 80)

results = []
grouped = df.groupby(["Year", "GrandPrix", "Driver", "Stint"])

for (year, gp, driver, stint), group in grouped:
    n_laps = len(group)
    
    # Only analyze stints with 10–20 laps
    if n_laps < 10 or n_laps > 20:
        continue

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        group["TyreLife"], group["LapTime"]
    )

    # Compute average track temperature for the stint
    avg_temp = group["TrackTemp"].mean()

    results.append(
        {
            "Year": year,
            "GrandPrix": gp,
            "Driver": driver,
            "Stint": int(stint),
            "n_laps": n_laps,
            "degradation_rate": slope,
            "r_squared": r_value**2,
            "correlation": r_value,
            "p_value": p_value,
            "std_err": std_err,
            "avg_track_temp": avg_temp,
        }
    )

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Sort by Driver (A–Z), then by Track Temperature (descending)
results_df = results_df.sort_values(
    by=["Driver", "avg_track_temp"], ascending=[True, False]
)

# Save results to CSV
results_df.to_csv("tyre_degradation_results_lap_cap_2023.csv", index=False)

print(f"\n" + "=" * 80)
print(f"\nDetailed results saved to 'tyre_degradation_results.csv' (2023, SOFT tyres, 10–20 laps only, sorted by driver and track temperature)")
print("\nAnalysis complete!")
