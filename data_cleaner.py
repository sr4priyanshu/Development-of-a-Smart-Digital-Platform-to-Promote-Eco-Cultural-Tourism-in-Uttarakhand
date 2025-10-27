import pandas as pd
import numpy as np
import os

def clean_tourism_data(input_filepath, output_filepath):
    """
    Cleans the raw tourism data from a CSV file and saves the cleaned data.

    This function performs several cleaning operations:
    - Sets a uniform header.
    - Trims leading/trailing whitespace from all data.
    - Handles missing 'Description' and 'Best_Time_to_Visit' with 'Not Available'.
    - Standardizes the 'Category' column to title case.
    - Converts 'Rating' to a numeric type, handling errors by setting invalid entries to NaN.
    - Fills missing numeric 'Rating' values with the median rating of the dataset.
    - Removes rows where critical information like 'Name' or 'District' is missing.
    - Resets the index of the final cleaned DataFrame.

    Args:
        input_filepath (str): The path to the raw CSV data file.
        output_filepath (str): The path where the cleaned CSV file will be saved.
    """
    print(f"Starting data cleaning process for '{input_filepath}'...")

    try:
        # Define column names to handle inconsistencies in CSV headers
        column_names = [
            'Name', 'District', 'Category', 'Description',
            'Rating', 'Best_Time_to_Visit', 'Latitude', 'Longitude'
        ]
        
        # Load the raw dataset
        # Use header=0 to use the first row as headers, names=column_names to overwrite them if needed.
        df = pd.read_csv(input_filepath, names=column_names, header=0)

        # 1. Trim whitespace from all string columns
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        # 2. Handle missing critical data: Drop rows if 'Name' or 'District' is missing
        df.dropna(subset=['Name', 'District'], inplace=True)

        # 3. Standardize text data: Convert 'Category' to Title Case
        df['Category'] = df['Category'].str.title()

        # 4. Handle missing non-critical text data with a placeholder
        df['Description'].fillna('Not Available', inplace=True)
        df['Best_Time_to_Visit'].fillna('Not Available', inplace=True)

        # 5. Clean and convert numeric data: 'Rating'
        # Convert 'Rating' to numeric, coercing errors into 'Not a Number' (NaN)
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
        
        # Calculate median rating, ignoring NaN values
        median_rating = df['Rating'].median()
        
        # Fill any remaining NaN ratings with the calculated median
        df['Rating'].fillna(median_rating, inplace=True)

        # 6. Clean and convert location data
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df.dropna(subset=['Latitude', 'Longitude'], inplace=True) # Drop if location is invalid

        # 7. Reset index after dropping rows
        df.reset_index(drop=True, inplace=True)

        # 8. Save the cleaned data to a new CSV file
        df.to_csv(output_filepath, index=False)

        print(f"Successfully cleaned data. Clean file saved to '{output_filepath}'.")
        print("\n--- Cleaning Summary ---")
        print(f"Original rows: {len(pd.read_csv(input_filepath))}")
        print(f"Cleaned rows: {len(df)}")
        print(f"Median rating used for missing values: {median_rating:.2f}")
        print("\n--- First 5 rows of cleaned data ---")
        print(df.head())
        print("\n--------------------------------------")


    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # Create a dummy raw CSV file for demonstration purposes
    raw_data = {
        'Name': ['  Rishikesh ', 'Nainital', 'Auli', 'Mussoorie ', 'Jim Corbett National Park', 'Valley of Flowers', 'Kedarnath', None, 'Badrinath'],
        'District': ['Dehradun', 'Nainital', 'Chamoli', 'Dehradun', 'Nainital', 'Chamoli', 'Rudraprayag', 'Pauri', 'Chamoli'],
        'Category': ['Spiritual', 'lake city', ' skiing destination ', 'Hill Station', 'National Park', 'trekking', 'Temple', 'Temple', 'Temple'],
        'Description': ['Yoga Capital', 'City of Lakes', 'Perfect for skiing', np.nan, 'Home to tigers', 'Alpine flowers', 'Lord Shiva Temple', 'A temple', 'Lord Vishnu Temple'],
        'Rating': ['4.8', '4.7', '4.9', '4.6', '4.8', 'invalid_rating', '4.9', '3.5', ''],
        'Best_Time_to_Visit': ['Sep-Mar', 'Mar-Jun', 'Nov-Mar', 'Sep-Jun', 'Nov-Jun', 'Jun-Oct', np.nan, 'All Year', 'May-Oct'],
        'Latitude': ['30.0869', '29.3919', '30.5332', '30.4598', '29.5305', '30.7266', '30.7352', '30.1473', '30.7433'],
        'Longitude': ['78.2676', '79.4542', '79.5638', '78.0644', '78.7748', '79.6053', '79.0669', '78.7766', '79.4938']
    }
    
    # Ensure the directory exists
    os.makedirs('data', exist_ok=True)
    
    raw_df = pd.DataFrame(raw_data)
    raw_filepath = 'data/raw_tourism_data.csv'
    cleaned_filepath = 'data/cleaned_tourism_data.csv'
    
    raw_df.to_csv(raw_filepath, index=False)
    
    # Run the cleaning function on the dummy file
    clean_tourism_data(raw_filepath, cleaned_filepath)
