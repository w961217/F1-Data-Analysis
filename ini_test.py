import fastf1 
import fastf1.plotting 
import matplotlib.pyplot as plt 
import pandas as pd 
import numpy as np 
from scipy.stats import linregress 

fastf1.plotting.setup_mpl(color_scheme='fastf1', misc_mpl_mods=False) 

year = 2025 
gp = 'Spain' 
session_type = 'R' 

session = fastf1.get_session(year, gp, session_type) 
session.load() 

laps = session.laps 
laps_cleaned = laps.loc[(laps['IsAccurate'] == True) &
                        (laps['LapTime'].notna()) & 
                        (laps['PitOutTime'].isna()) & 
                        (laps['PitInTime'].isna()) & 
                        (laps['TrackStatus'] == '1')].copy()

laps_cleaned['LapTimeSeconds'] = laps_cleaned['LapTime'].dt.total_seconds()

# Get a unique list of drivers participating in the race
drivers = pd.unique(laps_cleaned['Driver'])

# Create a figure and axes for the degradation analysis plot
fig, ax = plt.subplots(figsize=(20, 10))

# Get the unique compounds used in the cleaned laps and their corresponding colors
# Use fastf1's plotting function to get accurate colors for each compound
compound_colors = {
    compound: fastf1.plotting.get_compound_color(compound, session=session)
    for compound in laps_cleaned['Compound'].unique()
}

# Create a list to store degradation data for the table
degradation_data = []

# Iterate over each driver to analyze their degradation by stint
for driver in drivers:
    driver_laps = laps_cleaned.loc[laps_cleaned['Driver'] == driver]

    # Iterate over each stint of the driver
    stints = driver_laps['Stint'].unique()
    for stint_number in stints:
        stint_laps = driver_laps.loc[driver_laps['Stint'] == stint_number].copy()

        # Ensure there are enough laps in the stint for analysis
        if len(stint_laps) < 3:  # We need at least 3 laps for a decent linear regression
            continue

        # Get the tire compound for this stint
        compound = stint_laps['Compound'].iloc[0]

        # Calculate the 'age' of the tire in the stint
        stint_laps['StintLapNumber'] = stint_laps['LapNumber'] - stint_laps['LapNumber'].min() + 1

        # Perform linear regression to estimate degradation
        # Regress LapTimeSeconds against StintLapNumber
        # Optional: Could filter for clean air laps here before regression if desired
        # stint_laps_clean_air = stint_laps[stint_laps['GapToPrev'] > pd.Timedelta(seconds=3)] # Example filter
        # if not stint_laps_clean_air.empty:
        #    slope, intercept, r_value, p_value, std_err = linregress(stint_laps_clean_air['StintLapNumber'], stint_laps_clean_air['LapTimeSeconds'])

        slope, intercept, r_value, p_value, std_err = linregress(stint_laps['StintLapNumber'], stint_laps['LapTimeSeconds'])

        # The 'slope' is the degradation per lap in seconds/lap
        degradation_rate = slope * 1000  # Convert to milliseconds per lap

        # Append the degradation data to the list
        degradation_data.append({
            'Driver': driver,
            'Stint': stint_number,
            'Compound': compound,
            'Degradation (ms/lap)': f"{degradation_rate:.1f}" # Format to 1 decimal place
        })

        # Plot the lap times for the stint without a label
        ax.plot(stint_laps['StintLapNumber'], stint_laps['LapTimeSeconds'],
                marker='o', linestyle='-',
                color=compound_colors[compound]) # Use compound_colors here

        # Plot the regression line without a label
        ax.plot(stint_laps['StintLapNumber'], intercept + slope * stint_laps['StintLapNumber'],
                linestyle='--', color=compound_colors[compound], alpha=0.6) # Use compound_colors here

# Set the title for the degradation chart (after the loop)
ax.set_title(f'Tire Degradation Analysis - {gp} GP {year}')
ax.set_xlabel('Laps in Stint')
ax.set_ylabel('Lap Time (seconds)')
# We remove the legend as we are showing the data in a table
# ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()

# Create a pandas DataFrame from the collected data
degradation_df = pd.DataFrame(degradation_data)

# Display the table
print("\nTire Degradation Summary:")
from IPython.display import display # Import display here if not already imported globally
display(degradation_df) # Use display for better table formatting in Jupyter/Colab

# --- Analysis of Vehicle Performance Impact (Example with telemetry) ---

# Select a specific driver and stint number for telemetry comparison
# Ideally, choose a long stint where degradation is clearly visible
target_driver = 'LEC' # Example: Charles Leclerc
target_stint_number = 2 # Example: Second stint of Leclerc

# Filter the cleaned laps to get the data for the target driver and stint
leclerc_stint = laps_cleaned.loc[(laps_cleaned['Driver'] == target_driver) &
                                  (laps_cleaned['Stint'] == target_stint_number)].copy()

# Check if the specified stint was found for the driver
if not leclerc_stint.empty:
    # Calculate the lap number within the stint, starting from 1
    leclerc_stint['StintLapNumber'] = leclerc_stint['LapNumber'] - leclerc_stint['LapNumber'].min() + 1

    # Select the first lap of the stint as the "fresh" lap
    lap_fresh = leclerc_stint.loc[leclerc_stint['StintLapNumber'] == leclerc_stint['StintLapNumber'].min()]
    # Select the last lap of the stint as the "degraded" lap
    lap_degraded = leclerc_stint.loc[leclerc_stint['StintLapNumber'] == leclerc_stint['StintLapNumber'].max()]

    # Check if both a fresh and a degraded lap were found
    if not lap_fresh.empty and not lap_degraded.empty:
        # Extract the single row DataFrames as Series
        lap_fresh = lap_fresh.iloc[0]
        lap_degraded = lap_degraded.iloc[0]

        tel_fresh = lap_fresh.get_telemetry()
        tel_degraded = lap_degraded.get_telemetry()

        # Ensure distances are comparable (optional, less critical for plotting vs. distance)
        # Note: This normalization is not strictly necessary for plotting Distance vs. Speed,
        # Brake, Throttle, or G-Forces, as long as you plot against the actual distance.
        # It would be relevant if you wanted to align laps of different lengths.
        # tel_fresh['Distance_Normalized'] = tel_fresh['Distance'] / tel_fresh['Distance'].max()
        # tel_degraded['Distance_Normalized'] = tel_degraded['Distance'] / tel_degraded['Distance'].max()


        plt.figure(figsize=(15, 10))

        # 1. Plot Speed telemetry
        plt.subplot(3, 1, 1) # Create the first subplot (out of 4 rows, 1 column, position 1)
        # Plot Speed vs. Distance for the fresh lap
        plt.plot(tel_fresh['Distance'], tel_fresh['Speed'], label=f'Lap {lap_fresh["LapNumber"]} (Fresh {lap_fresh["Compound"]})', color='blue')
        # Plot Speed vs. Distance for the degraded lap
        plt.plot(tel_degraded['Distance'], tel_degraded['Speed'], label=f'Lap {lap_degraded["LapNumber"]} (Degraded {lap_degraded["Compound"]})', color='red')
        plt.title('Speed') # Set the title for the subplot
        plt.ylabel('Speed (km/h)') # Set the y-axis label
        plt.grid(True) # Add a grid
        plt.legend() # Add a legend

        # 2. Plot Brake telemetry (indicating braking points)
        plt.subplot(3, 1, 2) # Create the second subplot
        # Plot Brake vs. Distance for the fresh lap
        plt.plot(tel_fresh['Distance'], tel_fresh['Brake'], label=f'Lap {lap_fresh["LapNumber"]} (Fresh)', color='blue')
        # Plot Brake vs. Distance for the degraded lap
        plt.plot(tel_degraded['Distance'], tel_degraded['Brake'], label=f'Lap {lap_degraded["LapNumber"]} (Degraded)', color='red')
        plt.title('Brake') # Set the title
        plt.ylabel('Brake (%)') # Set the y-axis label
        plt.grid(True) # Add a grid
        plt.legend() # Add a legend

        # 3. Plot Throttle telemetry (indicating acceleration)
        plt.subplot(3, 1, 3) # Create the third subplot
        # Plot Throttle vs. Distance for the fresh lap
        plt.plot(tel_fresh['Distance'], tel_fresh['Throttle'], label=f'Lap {lap_fresh["LapNumber"]} (Fresh)', color='blue')
        # Plot Throttle vs. Distance for the degraded lap
        plt.plot(tel_degraded['Distance'], tel_degraded['Throttle'], label=f'Lap {lap_degraded["LapNumber"]} (Degraded)', color='red')
        plt.title('Acceleration') # Set the title
        plt.ylabel('Acceleration (%)') # Set the y-axis label
        plt.grid(True) # Add a grid
        plt.legend() # Add a legend


        # Set a main title for the entire set of telemetry subplots
        plt.suptitle(f'Telemetry Comparison: Fresh vs. Degraded Tires for {target_driver}', y=1.02)
        # Adjust subplots for a tight layout
        plt.tight_layout()
        # Display the telemetry comparison plots
        plt.show()
    else:
        # Print a message if fresh or degraded laps were not found in the stint
        print("Could not find fresh and degraded laps for the specified stint.")
else:
    # Print a message if the specified stint was not found for the driver
    print(f"Stint {target_stint_number} not found for driver {target_driver}.")
    