import pandas as pd

def clean_roster_data(file_path, output_path):
    # Load the CSV file
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # Identify the correct header row (Row index 2 contains actual column names)
    df.columns = df.iloc[2]
    df = df[3:].reset_index(drop=True)
    
    # Rename key columns
    df.rename(columns={df.columns[0]: "Team", df.columns[1]: "User ID", df.columns[2]: "Full Name"}, inplace=True)
    
    # Drop any fully empty columns
    df = df.dropna(axis=1, how='all')
    
    # Reset index
    df = df.reset_index(drop=True)
    
    # Convert dates to datetime format where applicable
    date_columns = [col for col in df.columns if '/' in str(col)]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
    
    # Save cleaned data to CSV
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Cleaned data saved to {output_path}")

# Example usage
input_file = "ADC_Roster.csv"  # Update with the actual file path
output_file = "Cleaned_ADC_Roster.csv"
clean_roster_data(input_file, output_file)
