from idlelib.iomenu import errors

import pandas as pd #working with tables like excel
from pathlib import Path #handle file paths
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent  # __file__ refers python file path C:\Users\rule_\Documents\Projects\AU_RE_Project\main.py
                                            # .resolve converts the path to absolute path
                                            # .parent refers the folder containing the python file
                                            # Base_Dir becomes C:\Users\rule_\Documents\Projects\AU_RE_Project --- avoiding hardcode full path -- gives flexibility to move path of project
RAW_DATA_PATH = BASE_DIR / "data_raw" / "NEM Generation Information Jan 2026.xlsx"

# function with try .... except block: If something fails (file missing, wrong sheet name, etc), Python jumps to except - handle error instead of crashing
# try - The code within this block is executed. If an exception occurs, the rest of the try block is skipped.
# except - This block catches and handles the specified exception

def load_raw_generation_data():
    try:
        df = pd.read_excel(RAW_DATA_PATH, sheet_name = "Generator Information", header = 3) # This is the core ingestion step.
        print("Raw data loaded successfully.")
        print(f"Shape: {df.shape}")  # (rows, columns)
        print(df.head())
        print("\n Column names: ")
        print(df.columns.tolist())    ## Get the column names as a list
        #print(f"DataFrame:\n{df}\n") # as dataframe
        return df
    except Exception as e:
        print(f"Error loading file: {e}")   # Prints the error nicely.

# ------------ Extract Only Useful Columns (Clean Layer Start) -----------
def clean_generation_data(df):
    # Step 1: Define important columns
    important_columns = [
        "DUID",
        "Site Name",
        "Region",
        "Technology Type",
        "Dispatch Type",
        "Unit Capacity (MW AC)",
        "Commitment Status",
        "Full Commercial Use Date",
        "Closure Date"
    ]

    # Step 2: Select only those columns
    df_clean = df[important_columns]

    # Step 3: Save clean dataset
    CLEAN_PATH = BASE_DIR / "data_clean" / "generation_clean_2026_01.csv"
    #CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)  #create the folder automatically is missing
    df_clean.to_csv(CLEAN_PATH, index=False) # index=False → prevents adding row numbers as a column

    print("Clean data saved.")
    print("\nClean dataset preview:")
    print(df_clean.head())
    print(df_clean.columns.tolist())
    return df_clean

# -------- Clean Data Validation -------
def validate_dataset(df):
    print("\n ============== Data Validation Report ==========")
    errors = []
    print(f"\nTotal rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # Check Columns
    required_columns = ["DUID", "Region","Unit Capacity (MW AC)", "Commitment Status", "Start Date" ]
    missing_cols = [col for col in required_columns
                    if col not in df.columns]

    if missing_cols:
        print(f"\nMissing required columns: {missing_cols}")
        errors.append(f"Missing columns: {missing_cols}")
        return errors  # stop further validation if schema broken

    print("\nAll required columns present.")

    # Duplicate check

    duplicate_count = df["DUID"].duplicated().sum()
    if duplicate_count > 0:
        print(f"\nDuplicate DUIDs found: {duplicate_count}")
        errors.append("Duplicate DUID detected.")
    else:
        print("\nNo duplicate DUIDs.")

    # --- Capacity Check ---
    invalid_capacity = (df["Unit Capacity (MW AC)"] <= 0).sum()
    if invalid_capacity > 0:
        print(f"\n❌ Invalid capacity rows (<=0): {invalid_capacity}")
        errors.append("Invalid capacity values found.")
    else:
        print("\n✔ All capacity values valid.")

    # --- Region Check ---
    valid_regions = ["NSW1", "QLD1", "VIC1", "SA1", "TAS1"]
    invalid_region_rows = (~df["Region"].isin(valid_regions)).sum()

    if invalid_region_rows > 0:
        print(f"\n❌ Invalid region rows: {invalid_region_rows}")
        errors.append("Invalid region detected.")
    else:
        print("\n✔ All regions valid.")

    # --- Status Check ---
    valid_status = ["Proposed", "Committed", "Operating"]
    invalid_status_rows = (~df["Commitment Status"].isin(valid_status)).sum()

    if invalid_status_rows > 0:
        print(f"\n❌ Invalid status rows: {invalid_status_rows}")
        errors.append("Invalid status found.")
    else:
        print("\n✔ All status values valid.")

    if not errors:
        print("\n🎉 VALIDATION PASSED – Dataset is clean.")
    else:
        print("\n⚠ VALIDATION FAILED – Issues detected.")

    print("\n========================================================\n")

    return errors

# ------------ Format extracted useful columns (clean layer) -----------
def format_data(df):
    # Step 4: missing values / blank
    print("\n Null values per column: ")
    print(df.isna().sum())  # .isna()- detect missing or "Not Available" (NA) values

    # Step 5: delete/drop missing values / blank
    df_clean = df.dropna(subset=["Site Name", "Region"])

    # Step 5: replace missing values / blank with "Text"
    df_clean["DUID"] = df_clean["DUID"].fillna("Unknown")
    df_clean["Commitment Status"] = df_clean["Commitment Status"].fillna("Publicly Announced")

    if df["DUID"].duplicated().any():
        df_clean = df.drop_duplicates(subset=["DUID"])

    # make region text Uppercase and remove spacing
    df_clean["Region"] = df_clean["Region"].str.strip().str.upper()

    # Step 6: convert date strings to date type - errors="coerce" -- As seen in the output, "not a date", "invalid", a NaN value, and the out-of-bounds date "1500-01-01" are all converted to NaT, while valid and parseable dates are converted correctly to datetime64[ns] objects
    df_clean["Full Commercial Use Date"] = pd.to_datetime(
        df_clean["Full Commercial Use Date"],
        errors="coerce"
    )

    df_clean["Closure Date"] = pd.to_datetime(
        df_clean["Closure Date"],
        errors="coerce"
    )


    print("\nData types after datetime conversion:")
    print(df_clean.dtypes)

    print("\n Values per column after formatting: ")
    print(df_clean.isna().sum())

    # Step 7: Extract only year
    df_clean["Full Commercial Use Date"] = df_clean["Full Commercial Use Date"].dt.year
    df_clean["Closure Year"] = df_clean["Closure Date"].dt.year

    # Step 6: Save clean-formatted dataset
    CLEAN_PATH = BASE_DIR / "data_clean" / "generation_clean_2026_01.csv"
    df_clean.to_csv(CLEAN_PATH, index=False)
    return df_clean


# ------------ Filter Operating Plants-----------

def filter_operating_plants(df):
    print("\nUnique Commitment Status values:")
    print(df["Commitment Status"].unique())

    print("\nCommitment Status distribution:")
    print(df["Commitment Status"].value_counts()) #df["Commitment Status"] → selects that column
                                                  #.value_counts() → counts how many times each status appears / pivot table

    # Define statuses considered operating
    operating_status = ["In Service", "In Commissioning"] # this creates python list

    df_operating = df[ df["Commitment Status"].isin(operating_status) ].copy() # .isin() checks: Is this value inside the list?
                                                                               # .copy() creates separate copy from the original dataframe to avoid error

    print("\nOperating plants only:")
    print("Shape:", df_operating.shape)

    # Optional: Save operating dataset
    OPERATING_PATH = BASE_DIR / "data_clean" / "generation_operating_2026_01.csv"
    df_operating.to_csv(OPERATING_PATH, index=False)

    #print(df_operating["Commitment Status"], df_operating["Unit Capacity (MW AC)"])
    print("\nTotal Operating Capacity (MW): ")
    print(df_operating["Unit Capacity (MW AC)"].sum())
    return df_operating

# ------ Operating Capacity by Region -----------
def capacity_by_region(df):
    # Group by Region and sum capacity
    df_region = (df.groupby("Region")["Unit Capacity (MW AC)"].sum()
                 .reset_index()) #used to reset the index of a DataFrame or Series to the default integer index (0, 1, 2, ...). It is particularly useful after operations like filtering, sorting, or grouping that may result in a non-sequential or custom index

    # Sort largest to smallest
    df_region = df_region.sort_values(by = "Unit Capacity (MW AC)",ascending=False) # ascending=False -> sort from large to small
                                                                                    #ascending = True -> sort small to large - DEFAULT

    # Calculate percentage share by region and create a new column ----
    total_capacity = df_region["Unit Capacity (MW AC)"].sum()
    df_region["Market Share %"] = df_region["Unit Capacity (MW AC)"] / total_capacity * 100

    # Add ranking
    df_region["Rank"] = df_region["Unit Capacity (MW AC)"].rank(
        method="dense",
        ascending=False
    ).astype(int)

    print("\nOperating Capacity by Region (MW): ")
    print(df_region[["Region", "Unit Capacity (MW AC)"]])

    print("\nOperating Capacity by Region (Professional View):")
    print(df_region)
    return df_region

# ---------- Break by technology type ----------------
def capacity_by_technology(df):
    df_technology = (df.groupby("Technology Type")["Unit Capacity (MW AC)"].sum().reset_index())
    df_technology = df_technology.sort_values(by = "Unit Capacity (MW AC)", ascending = False )
    print("\nOperating Capacity by Technology (MW): ")
    print(df_technology)
    return df_technology

# -------- Final Reporting Format-----------------
def reporting_format(df):
    # Remove last character from region column
    df_region_reporting = df
    # Remove the trailing number (e.g., NSW1 → NSW)
    df_region_reporting["Region"] = df_region_reporting["Region"].str[:-1]
    df_region_reporting = df_region_reporting.rename(
        columns={"Unit Capacity (MW AC)": "Capacity (MW)"}
    )
    #: → formatting start , → add thousands separator .2f → show 2 decimal places ---- .map("{:,.2f}".format) They become STRINGS, not numbers anymore.
    df_region_reporting["Capacity (MW)"] = df_region_reporting["Capacity (MW)"].map("{:,.2f}".format)
    print("\nReport for presentation: ")
    print(df_region_reporting)
    return df_region_reporting

# ------ Plot -----
def plot_capacity_by_region(df):

    # Make sure region names are clean
    df_plot = df.copy()
    df_plot["Region"] = df_plot["Region"].str[:-1]

    # Sort properly
    df_plot = df_plot.sort_values(
        by="Unit Capacity (MW AC)",
        ascending=False
    )

    # Create figure
    plt.figure()

    # Create bar chart
    plt.bar(
        df_plot["Region"],
        df_plot["Unit Capacity (MW AC)"]
    )

    # Add labels
    plt.xlabel("Region")
    plt.ylabel("Capacity (MW)")
    plt.title("Operating Capacity by Region (NEM)")

    # Rotate x labels if needed
    plt.xticks(rotation=45)

    # Create output folder if it doesn't exist
    output_dir = BASE_DIR  / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save image
    save_path = output_dir / "operating_capacity_by_region_2026_01.png"
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    print(f"\nChart saved to: {save_path}")
    # Show plot
    plt.show()

# Only run this function if this file is executed directly ---- MAIN BLOCK
if __name__ == "__main__": # here main is the main function/module, file or folder that is set to execute first -- then submodule
    # load raw data
    df_raw = load_raw_generation_data()
    #load clean data
    df_clean = clean_generation_data(df_raw)
    # Data Validate
    errors = validate_dataset(df_clean)
    if errors:
        print("Errors found:", errors)
    else:
        print("Dataset ready for production.")


    #load clean - formatted data
    df_format = format_data(df_clean)
    #load operating data - filtered
    df_operating = filter_operating_plants(df_format)
    # Analysis capacity by region and technology
    df_region_capacity = capacity_by_region(df_operating)
    df_technology_capacity = capacity_by_technology(df_operating)

    df_report = reporting_format(df_region_capacity)
    plot_capacity_by_region(df_region_capacity)



# ----- Geospatial example -----
from geospatial import add_fake_coordinates, convert_to_geodataframe, plot_projects_map, export_to_geojson

df_operating = add_fake_coordinates(df_operating)

gdf_projects = convert_to_geodataframe(df_operating)
plot_projects_map(gdf_projects)
export_to_geojson(gdf_projects)




