import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# Create a connection to SQLite database
conn = sqlite3.connect('example/donation_system.db')

# Sample DataFrames
organizations_data = {
    'org_id': ['org1', 'org2', 'org3'],
    'name': ['Global Relief', 'Local Support', 'Medical Aid'],
    'location': ['New York', 'London', 'Tokyo'],
    'contact_email': ['contact@gr.org', 'help@ls.org', 'info@ma.org']
}

resources_data = {
    'resource_id': ['r1', 'r2', 'r3', 'r4'],
    'name': ['Food Supplies', 'Medical Kits', 'Clothing', 'Books'],
    'category': ['Food', 'Medical', 'Clothing', 'Education'],
    'unit': ['boxes', 'kits', 'pieces', 'sets']
}

donations_data = {
    'donation_id': range(1, 6),
    'org_id': ['org1', 'org2', 'org1', 'org3', 'org2'],
    'resource_id': ['r1', 'r2', 'r3', 'r1', 'r4'],
    'quantity': [100, 50, 200, 150, 75],
    'date': ['2024-01-15', '2024-01-16', '2024-01-15', '2024-01-17', '2024-01-16'],
    'status': ['received', 'in_transit', 'received', 'pending', 'received']
}

# Create DataFrames
organizations_df = pd.DataFrame(organizations_data)
resources_df = pd.DataFrame(resources_data)
donations_df = pd.DataFrame(donations_data)

# Save DataFrames to SQLite database
organizations_df.to_sql('organizations', conn, if_exists='replace', index=False)
resources_df.to_sql('resources', conn, if_exists='replace', index=False)
donations_df.to_sql('donations', conn, if_exists='replace', index=False)

# Example queries using pandas
print("\nOrganizations:")
print(pd.read_sql('SELECT * FROM organizations', conn))

print("\nResources:")
print(pd.read_sql('SELECT * FROM resources', conn))

# Complex queries
print("\nDonation Summary by Organization:")
query1 = """
SELECT o.name as organization, SUM(d.quantity) as total_donations
FROM donations d
JOIN organizations o ON d.org_id = o.org_id
GROUP BY o.name
"""
donation_summary = pd.read_sql(query1, conn)
print(donation_summary)

print("\nResource Distribution:")
query2 = """
SELECT r.category, SUM(d.quantity) as total_quantity
FROM donations d
JOIN resources r ON d.resource_id = r.resource_id
GROUP BY r.category
"""
resource_dist = pd.read_sql(query2, conn)
print(resource_dist)

# Visualization of donation summary
plt.figure(figsize=(10, 6))
donation_summary.plot(x='organization', y='total_donations', kind='bar')
plt.title('Total Donations by Organization')
plt.xlabel('Organization')
plt.ylabel('Total Quantity')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../example/org_donations.png')
plt.close()

# Visualization of resource distribution
plt.figure(figsize=(10, 6))
resource_dist.plot(x='category', y='total_quantity', kind='pie', autopct='%1.1f%%')
plt.title('Distribution of Resources by Category')
plt.axis('equal')
plt.savefig('../example/resource_distribution.png')
plt.close()

# Advanced analysis
print("\nDonation Trends:")
donations_df['date'] = pd.to_datetime(donations_df['date'])
daily_donations = donations_df.groupby('date')['quantity'].sum()
print(daily_donations)

# Status analysis
print("\nDonation Status Summary:")
status_summary = pd.read_sql("""
SELECT status, COUNT(*) as count, SUM(quantity) as total_quantity
FROM donations
GROUP BY status
""", conn)
print(status_summary)

# Export query results to CSV
donation_summary.to_csv('../example/donation_summary.csv', index=False)
resource_dist.to_csv('../example/resource_distribution.csv', index=False)
status_summary.to_csv('../example/status_summary.csv', index=False)

# Close connection
conn.close()

print("\nAnalysis complete! Data has been processed and exported to CSV files.")
print("Database operations completed successfully.")