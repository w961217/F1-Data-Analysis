import csv

# Change these to your actual file and column name/index
csv_file = r'C:\Users\wesle\Programming\Python\F1-Data-Analysis\csv\correlation_tests\tyre_degradation_results_2.0.csv'
column_name = 'correlation'  # or set to None and use column_index instead
column_index = None    # e.g. 2 if using index instead of name

count = 0

with open(csv_file, 'r', newline='') as file:
    reader = csv.DictReader(file) if column_name else csv.reader(file)
    
    for row in reader:
        # Get value depending on how we're reading
        value = row[column_name] if column_name else row[column_index]
        
        try:
            num = float(value)
            if num > 0:
                count += 1
        except ValueError:
            # Skip non-numeric values
            continue

print(f"Number of positive numbers in column '{column_name or column_index}': {count}")
