import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('example/sample.csv')

# Display basic information about the dataset
print("\nDataset Info:")
print(df.info())

# Show the first few rows
print("\nFirst few rows of the dataset:")
print(df.head())

# Basic statistics of numerical columns
print("\nNumerical Statistics:")
print(df.describe())

# Count of donations by resource type
print("\nDonations by Resource Type:")
resource_counts = df['resource_type'].value_counts()
print(resource_counts)

# Total quantity by status
print("\nTotal Quantity by Status:")
status_quantity = df.groupby('status')['quantity'].sum()
print(status_quantity)

# Average donation quantity by location
print("\nAverage Donation Quantity by Location:")
location_avg = df.groupby('location')['quantity'].mean()
print(location_avg)

# Create a bar plot of total quantities by resource type
plt.figure(figsize=(12, 6))
df.groupby('resource_type')['quantity'].sum().plot(kind='bar')
plt.title('Total Quantity by Resource Type')
plt.xlabel('Resource Type')
plt.ylabel('Total Quantity')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('example/resource_quantity_plot.png')
plt.close()