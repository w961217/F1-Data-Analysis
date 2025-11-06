import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import os
import itertools

# Folder containing your saved driver-year CSV files
data_dir = r"C:\Users\wesle\Programming\Python\F1-Data-Analysis\csv\driver_results_year"

# Collect all CSV files
csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

if not csv_files:
    print("No CSV files found in the specified directory.")
    exit()

# Combine all driver-year CSVs into one DataFrame
dataframes = []
for file in csv_files:
    file_path = os.path.join(data_dir, file)
    try:
        df = pd.read_csv(file_path)
        dataframes.append(df)
    except Exception as e:
        print(f"Skipping {file}: {e}")

combined_df = pd.concat(dataframes, ignore_index=True)

# ====== FILTER FOR YEARS 2022 TO 2024 ======
combined_df = combined_df[(combined_df["Year"] >= 2022) & (combined_df["Year"] <= 2024)]

print(f"Loaded {len(csv_files)} CSV files — {len(combined_df)} rows after filtering for 2022-2024.")
print(f"Drivers: {combined_df['Driver'].nunique()} | Years: {combined_df['Year'].nunique()}")

# Create output folder for plots
plot_dir = os.path.join(data_dir, "plots")
os.makedirs(plot_dir, exist_ok=True)

# ========== COMBINED TRENDLINE GRAPH ==========
plt.figure(figsize=(12, 8))
colors = itertools.cycle(plt.cm.tab20.colors)

for (driver, year), group in combined_df.groupby(["Driver", "Year"]):
    if len(group) < 2:
        continue

    x = group["avg_track_temp"]
    y = group["degradation_rate"]

    # Linear regression for this driver-year
    slope, intercept, r_value, _, _ = stats.linregress(x, y)
    x_line = pd.Series(sorted(x))
    y_line = intercept + slope * x_line

    color = next(colors)
    label = f"{driver} ({year})  r={r_value:.2f}"

    plt.scatter(x, y, color=color, s=30)
    plt.plot(x_line, y_line, color=color, label=label, linewidth=1.5)

plt.title("Track Temperature vs Tyre Degradation Rate (All Drivers, 2022 - 2024)")
plt.xlabel("Average Track Temperature / degrees Celsius")
plt.ylabel("Tyre Degradation") 
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(fontsize=8, loc="best", ncol=2)
plt.tight_layout()

# Save the plot
combined_plot_path = os.path.join(plot_dir, "all_drivers_2022_2024_trend.png")
plt.savefig(combined_plot_path, dpi=300)
plt.close()

print(f"\nSaved combined trendline graph to:\n{combined_plot_path}")
