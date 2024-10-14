# $env:PYTHONDONTWRITEBYTECODE = 1
import csv

input_file = r'data\test\data.csv'
output_file = 'cleaned_file.csv'

with open(input_file, 'r') as csvfile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(csvfile)
    writer = csv.writer(outfile)
    
    for row in reader:
        # Check if row has more than 2 fields
        if len(row) > 2:
            # Join all columns except the last one and enclose them in quotes
            examples = ','.join(row[:-1])
            label = row[-1]
            fixed_row = [f'"{examples}"', label]  # Put the examples in quotes and keep the label
            writer.writerow(fixed_row)
        else:
            # Write rows that already have 2 columns as is
            writer.writerow(row)

print(f"Fixed file saved as {output_file}")


# 55.5 4000 WALA
# 60 3000 WALA
# 66.38 2390 WALA