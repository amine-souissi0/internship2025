import pandas as pd
from tabulate import tabulate
import ace_tools as tools

# Load the CSV file
file_path = "/mnt/data/ADC_Roster.csv"
df = pd.read_csv(file_path, encoding="utf-8", delimiter=",")  # Adjust delimiter if needed

# Drop completely empty columns
df.dropna(how='all', axis=1, inplace=True)

# Drop unnecessary header rows
df_cleaned = df.iloc[2:].reset_index(drop=True)

# Rename columns based on the first meaningful row
df_cleaned.columns = df_cleaned.iloc[0]
df_cleaned = df_cleaned[1:].reset_index(drop=True)

# Display the cleaned dataframe in a readable format
tools.display_dataframe_to_user(name="Cleaned Shift Schedule", dataframe=df_cleaned)
