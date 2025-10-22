import pandas as pd
from scipy import stats

# Load the data
df = pd.read_csv(r"C:\Users\wesle\Programming\Python\F1-Data-Analysis\csv\fastf1_lap_data.csv") 

# Clean the data
df = df.dropna(subset=["TyreLife", "LapTime", "Compound"])
df = df[df["LapTime"] > 0]

# Filter for SOFT compound only
df = df[df["Compound"] == "SOFT"]

print("Dataset Overview (SOFT tyres only):")
print(f"Total laps analyzed: {len(df):,}")
print(f"Years covered: {sorted(df['Year'].unique())}")
print(f"Grand Prix events: {df['GrandPrix'].nunique()}")
print(f"Drivers: {df['Driver'].nunique()}")
print("\n" + "=" * 80 + "\n")

# Analyze by Year, Grand Prix, Driver, and Stint
print("ANALYSIS BY YEAR, GRAND PRIX, DRIVER, AND STINT (SOFT tyres, >15 laps):")
print("-" * 80)

results = []
grouped = df.groupby(["Year", "GrandPrix", "Driver", "Stint"])

for (year, gp, driver, stint), group in grouped:
    # Only analyze stints with more than 15 laps
    if len(group) < 5:
        continue

    # Use scipy linregress
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        group["TyreLife"], group["LapTime"]
    )

    results.append(
        {
            "Year": year,
            "GrandPrix": gp,
            "Driver": driver,
            "Stint": int(stint),
            "n_laps": len(group),
            "degradation_rate": slope,
            "r_squared": r_value**2,
            "correlation": r_value,
            "p_value": p_value,
            "std_err": std_err,
        }
    )

results_df = pd.DataFrame(results)

# Save results to CSV
results_df.to_csv("tyre_degradation_results.csv", index=False)
print(f"\n" + "=" * 80)
print(f"\nDetailed results saved to 'tyre_degradation_results.csv'")
print("\nAnalysis complete!") 

