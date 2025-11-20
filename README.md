The script reads a raw tourism dataset (CSV/Excel), cleans it, saves the cleaned file, and uploads it to a Supabase database.

1. Supabase Setup

Initializes a Supabase client using URL + API key.

If initialization fails, upload is skipped.

2. File Reading

_read_tabular_file() reads .xlsx, .xls, or .csv automatically.

3. Data Cleaning (clean_tourism_data)

Loads raw data with fixed column names.

Removes extra spaces and unwanted characters.

Cleans Name and Category fields.

Drops rows missing essential fields (Name, District).

Fills missing descriptions with "Not Available".

Converts Rating to numeric and fills missing values using median.

Converts and validates Latitude and Longitude; drops invalid rows.

Resets index and saves cleaned data to /data/cleaned_tourism_data.csv.

4. Uploading to Supabase

Converts dataframe to list of dictionaries.

Replaces NaN with None.

Uses upsert() to insert/update records in the destinations table.

5. Main Execution

Automatically finds file paths.

Ensures /data folder exists.

Runs the cleaning + uploading process.
