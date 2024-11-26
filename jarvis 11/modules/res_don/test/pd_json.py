import pandas as pd
import json
import matplotlib.pyplot as plt
from datetime import datetime

# Load the JSON file
with open('example/sample.json', 'r') as file:
    data = json.load(file)

# Create DataFrames for different sections
organizations_df = pd.DataFrame(data=data["organizations"])
print(organizations_df.head())
