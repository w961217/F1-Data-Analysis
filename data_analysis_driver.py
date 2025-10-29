import pandas as pd
from scipy import stats
import os

# Load the data
df = pd.read_csv(
    r"C:\Users\wesle\Programming\Python\F1-Data-Analysis\csv\fastf1_lap_data.csv"
)

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

# Create output folder
output_dir = "driver_results"
os.makedirs(output_dir, exist_ok=True)

print("ANALYSIS BY YEAR, GRAND PRIX, DRIVER, AND STINT (SOFT tyres, >10 laps):")
print("-" * 80)

# Group by driver
for driver, driver_df in df.groupby("Driver"):
    results = []

    grouped = driver_df.groupby(["Year", "GrandPrix", "Stint"])
    for (year, gp, stint), group in grouped:
        # Only analyze stints with more than 10 laps
        if len(group) < 10:
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
                "n_laps": len(group),
                "degradation_rate": slope,
                "r_squared": float(r_value) ** 2, 
                "correlation": r_value,
                "p_value": p_value,
                "std_err": std_err,
                "avg_track_temp": avg_temp,
            }
        )

    # Skip if no valid stints
    if not results:
        continue

    # Convert to DataFrame and sort
    driver_results_df = pd.DataFrame(results)
    driver_results_df = driver_results_df.sort_values(
        by="avg_track_temp", ascending=False
    )

    # Save each driver's results to a separate CSV
    safe_driver_name = str(driver).replace(" ", "_").replace("/", "_")
    output_path = os.path.join(output_dir, f"{safe_driver_name}_tyre_degradation.csv")
    driver_results_df.to_csv(output_path, index=False)

    print(f"Saved results for {driver}: {output_path}")

print(f"\n" + "=" * 80)
print(f"\nDetailed results saved to '{output_dir}/' — one file per driver")
print("\nAnalysis complete!")
