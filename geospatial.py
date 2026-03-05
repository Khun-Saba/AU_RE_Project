import numpy as np
import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import Point
from pathlib import Path #handle file paths

def add_fake_coordinates(df):
    """
    Add fake lat/lon based on NEM region.
    """

    # Approximate central coordinates of each region in Python Dictionary
    region_coordinates = {
        "NSW1": (-33.0, 147.0),
        "QLD1": (-21.0, 145.0),
        "VIC1": (-37.0, 145.0),
        "SA1": (-30.0, 135.0),
        "TAS1": (-42.0, 147.0),
    }

    # Create empty columns to create spatial information
    df["Latitude"] = None
    df["Longitude"] = None

    # ---------------- Create clustered but slightly spread points.

    for region, (lat, lon) in region_coordinates.items():
        mask = df["Region"] == region  # here mask creates a filter like excel file - If region = NSW 1 then filter those rows

        # Add small random noise (+/- 1 degree)
        # mask.sum() -  Counts how many plants are in that region.
        # Example: NSW1 has 25 plants → mask.sum() = 25
        # np.random.uniform(-1, 1, mask.sum()) - Creates 25 random numbers between: -1 to 1
        df.loc[mask, "Latitude"] = lat + np.random.uniform(-1, 1, mask.sum())
        df.loc[mask, "Longitude"] = lon + np.random.uniform(-1, 1, mask.sum())

    print("\nFake coordinates added.")
    return df

# This function converts a normal pandas DataFrame into a GeoDataFrame (spatial dataframe). Excel table ➜ Spatial table with map intelligence
def convert_to_geodataframe(df):

    required_columns = ["Latitude", "Longitude"]

    for col in required_columns:
        if col not in df.columns:   # data validation check - “Before I build geometry, make sure lat/long columns exist.”
            raise ValueError(f"Missing required column: {col}")

    geometry = [
        Point(xy) for xy in zip(df["Longitude"], df["Latitude"])  # geometric object - zip(df["Longitude"], df["Latitude"]) pairs (Longitude, Latitude) then move to Point(x,y) to create POINT (147.2 -33.1)
    ]

    gdf = gpd.GeoDataFrame(
        df,
        geometry=geometry,  # create new geometry column
        crs="EPSG:3577"   #CRS = Coordinate Reference System, EPSG:4326 is in degrees global google map system
    )                      #  crs="EPSG:3577" for Australia distance calculation

    print("\nConverted to GeoDataFrame.")
    print(gdf.head())
    return gdf

def plot_projects_map(gdf):

    ax = gdf.plot()

    ax.set_title("Energy Projects Map")
    plt.show()   # <-- REQUIRED in PyCharm

    print("Map plotted successfully.")

def export_to_geojson(gdf):
    # Create output folder
    BASE_DIR = Path(__file__).resolve().parent
    output_dir = BASE_DIR / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Specify file name and folder
    save_path = output_dir / "operating_plants_2026_01.geojson"
    gdf.to_file(save_path, driver="GeoJSON")

    print(f"GeoJSON exported successfully to: {save_path}")

