import pandas as pd
from scipy import stats
import os

# Load the data
df = pd.read_csv(r"C:\Users\wesle\Programming\Python\F1-Data-Analysis\csv\fastf1_lap_data.csv")

# Clean the data
df = df.dropna(subset=["TyreLife", "LapTime", "Compound", "TrackTemp"])
df = df[df["LapTime"] > 0]

# Filter for SOFT compound only
df = df[df["Compound"] == "SOFT"]

print("Dataset Overview (SOFT tyres only):")
print(f"Total laps analyzed: {len(df):,}")
print(f"Years covered: {sorted(df['Year'].unique())}")
print(f"Grand Prix events: {df['GrandPrix'].nunique()}")
print(f"Drivers: {df['Driver'].nunique()}")
print("\n" + "=" * 80 + "\n")

print("ANALYSIS BY YEAR, GRAND PRIX, DRIVER, AND STINT (SOFT tyres, 10–20 laps):")
print("-" * 80)

results = []
grouped = df.groupby(["Year", "GrandPrix", "Driver", "Stint"])

for (year, gp, driver, stint), group in grouped:
    # Only analyze stints with 10–20 laps
    if len(group) < 10 or len(group) > 20:
        continue

    # Perform linear regression: only slope and standard error
    slope, _, _, _, std_err = stats.linregress(group["TyreLife"], group["LapTime"])

    # Compute average track temperature for the stint
    avg_temp = group["TrackTemp"].mean()

    results.append(
        {
            "Year": year,
            "GrandPrix": gp,
            "Driver": driver,
            "Stint": int(stint),
            "n_laps": len(group),
            "degradation_rate": slope,
            "std_err": std_err,
            "avg_track_temp": avg_temp,
        }
    )

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Sort by Driver, then Year, then Track Temperature (descending)
results_df = results_df.sort_values(
    by=["Driver", "Year", "avg_track_temp"], ascending=[True, True, False]
)

# Create output folder
output_dir = "driver_results_year"
os.makedirs(output_dir, exist_ok=True)

# Export one CSV per driver per year
for (driver, year), driver_year_data in results_df.groupby(["Driver", "Year"]):
    safe_driver_name = str(driver).replace(" ", "_").replace("/", "_")
    filename = os.path.join(output_dir, f"tyre_degradation_{safe_driver_name}_{year}.csv")
    driver_year_data.to_csv(filename, index=False)
    print(f"Saved {filename} ({len(driver_year_data)} rows)")

print(f"\n" + "=" * 80)
print(f"\nDetailed degradation-rate results with std_err saved to '{output_dir}/' — one file per driver per year")
print("\nAnalysis complete!")
