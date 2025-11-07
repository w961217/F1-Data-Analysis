import pandas as pd

# Path to your CSV file
csv_file = r"C:\Users\wesle\Programming\Python\F1-Data-Analysis\csv\fastf1_lap_data.csv"

# Load the CSV
data = pd.read_csv(csv_file)

# Make sure there's a column that indicates the year (replace 'Year' with your actual column name)
# Filter for years 2022–2024
filtered_data = data[data['Year'].isin([2022, 2023, 2024])]

# Export filtered data to a new CSV
output_file = r"C:\Users\wesle\Programming\Python\F1-Data-Analysis\csv\fastf1_lap_data_2022_2024.csv"
filtered_data.to_csv(output_file, index=False)

print(f"Filtered data exported to {output_file}")
