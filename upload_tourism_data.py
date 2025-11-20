import pandas as pd
import numpy as np
import os
from pathlib import Path
from supabase import create_client, Client

SUPABASE_URL = "https://uzersrwjelicaujpoxod.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6ZXJzcndqZWxpY2F1anBveG9kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2NDkzMzQsImV4cCI6MjA3NzIyNTMzNH0.-HCZIBi-CAE4xkEfA6E9Fx_EgINsr2Lz0CTW4MjO4TU"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Supabase client initialized successfully.")
except Exception as e:
    print("[ERROR] Failed to initialize Supabase client:", e)
    supabase = None

# --- End of Supabase Setup ---


def upload_to_supabase(df):
    """Upload cleaned dataframe to Supabase table."""
    # Skip upload if client wasn't initialized
    if supabase is None:
        print("Supabase client not initialized. Skipping upload.")
        return

    try:
        # Convert DataFrame to list of dictionaries
        data = df.to_dict(orient="records")
        
        # Supabase (and JSON) prefers 'None' (null) over 'NaN'
        for row in data:
            if 'Latitude' in row and pd.isna(row['Latitude']):
                row['Latitude'] = None
            if 'Longitude' in row and pd.isna(row['Longitude']):
                row['Longitude'] = None

        if not data:
            print("[WARN] No cleaned rows to upload. Skipping Supabase upsert.")
            return

        print(f"Attempting to upload {len(data)} records to 'destinations' table...")
        
        # Use upsert() to insert new rows or update existing ones
        response = supabase.table("destinations").upsert(data).execute()
        
        if response.data:
            print(f"[OK] Successfully uploaded to Supabase: {len(response.data)} records")
        else:
            # Handle cases where the API call succeeded but no data was returned
            print(f"[WARN] Supabase upload completed but returned no data. Response: {response}")
            if response.error:
                print(f"   Error details: {response.error}")

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during Supabase upload: {e}")


def _read_tabular_file(filepath, **kwargs):
    suffix = Path(filepath).suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(filepath, **kwargs)
    return pd.read_csv(filepath, **kwargs)


def clean_tourism_data(input_filepath, output_filepath):
 
    print(f"Starting data cleaning process for '{input_filepath}'...")
    
    original_row_count = 0
    median_rating = np.nan # Initialize median_rating

    try:
        # Read the file once just to get the original row count
        try:
            original_row_count = len(_read_tabular_file(input_filepath))
        except Exception:
            pass # Will be caught by the main FileNotFoundError

        # Define column names to handle inconsistencies in CSV headers
        column_names = [
            'Name', 'District', 'Category', 'Description',
            'Rating', 'Best_Time_to_Visit', 'Latitude', 'Longitude'
        ]
        
        # Load the raw dataset
        # Use header=0 to use the first row as headers, names=column_names to overwrite them.
        df = _read_tabular_file(input_filepath, names=column_names, header=0)

        # 1. Trim whitespace from string values without disturbing numeric data
        df = df.map(lambda value: value.strip() if isinstance(value, str) else value)

        # 1b. Remove unnecessary commas within the Name field
        df['Name'] = (
            df['Name']
            .astype(str)
            .str.replace(r"\s*,\s*", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # 2. Handle missing critical data: Drop rows if 'Name' or 'District' is missing
        df.dropna(subset=['Name', 'District'], inplace=True)

        # 3. Standardize text data: Convert 'Category' to Title Case
        # Use .astype(str) to avoid errors if a category is somehow numeric
        df['Category'] = (
            df['Category']
            .fillna('')
            .astype(str)
            .str.replace(r"[,\|\@\#\%\^\*\~\`\$<>/\\]+", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .str.title()
        )

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
        # Drop if location is invalid, as it's critical for a map
        df.dropna(subset=['Latitude', 'Longitude'], inplace=True) 

        # 7. Reset index after dropping rows
        df.reset_index(drop=True, inplace=True)

        # 8. Save the cleaned data to a new CSV file
        df.to_csv(output_filepath, index=False)

        print(f"Successfully cleaned data. Clean file saved to '{output_filepath}'.")
        print("\n--- Cleaning Summary ---")
        print(f"Original rows: {original_row_count}")
        print(f"Cleaned rows: {len(df)}")
        if not np.isnan(median_rating):
            print(f"Median rating used for missing values: {median_rating:.2f}")
        else:
            print("Median rating could not be calculated (no valid ratings).")
        print("\n--- First 5 rows of cleaned data ---")
        print(df.head())
        print("\n--------------------------------------")
        
        # --- 9. Upload cleaned data to Supabase ---
        # Standardize column names to lowercase and underscores
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        print("\n--- Starting Supabase Upload ---")
        upload_to_supabase(df)
        print("--------------------------------------")


    except FileNotFoundError:
        print(f"[ERROR] The file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during cleaning: {e}")


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent
    raw_filepath = base_dir / "raw_tourism_data.xlsx"
    cleaned_dir = base_dir / "data"
    cleaned_dir.mkdir(exist_ok=True)
    cleaned_filepath = cleaned_dir / "cleaned_tourism_data.csv"

    clean_tourism_data(str(raw_filepath), str(cleaned_filepath))