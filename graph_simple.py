import pandas as pd
import matplotlib.pyplot as plt
import os
import itertools
from matplotlib import cm

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

# ========== SCATTER GRAPH (NO TRENDLINES) ==========
plt.figure(figsize=(12, 8))

cmap = cm.get_cmap("tab20")
colors = itertools.cycle(cmap.colors)
legend_handles = []

for (driver, year), group in combined_df.groupby(["Driver", "Year"]):
    x = group["avg_track_temp"]
    y = group["degradation_rate"]

    color = next(colors)
    label = f"{driver} ({year})"
    scatter = plt.scatter(x, y, color=color, s=30, label=label)
    legend_handles.append((scatter, label))

plt.title("Relationship Between Track Temperature and Tyre Degradation (All Drivers, 2022 - 2024)")
plt.xlabel("Average Track Temperature / degrees Celsius")
plt.ylabel("Tyre Degradation")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

# Save main graph without legend
graph_path = os.path.join(plot_dir, "all_drivers_2022_2024_raw_points.png")
plt.savefig(graph_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved main graph (no legend): {graph_path}")

# ========== SEPARATE LEGEND IMAGE ==========
fig_legend = plt.figure(figsize=(10, len(legend_handles) * 0.25))
plt.axis("off")

handles, labels = zip(*legend_handles)
fig_legend.legend(
    handles,
    labels,
    loc="center",
    fontsize=8,
    frameon=False,
    ncol=2
)

legend_path = os.path.join(plot_dir, "all_drivers_2022_2024_raw_points_legend.png")
fig_legend.savefig(legend_path, dpi=300, bbox_inches="tight")
plt.close(fig_legend)

print(f"Saved separate legend image: {legend_path}")
