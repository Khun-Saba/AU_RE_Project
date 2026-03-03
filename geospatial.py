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

#for loop - each item in region_coordinates dictionary For each item in the dictionary:
                    # region = "NSW1"
                    # lat = -33.0
                    # lon = 147.0
                    # Then next loop:
                    # region = "QLD1"
                    # lat = -21.0
                    # lon = 145.0
                    # And so on.

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

# ------- Distance between points ----------------
def calculate_distances(gdf):
    """
    Calculate distance between each plant and every other plant (meters).
    """

    # Convert to projected CRS (meters from degree)
    gdf_projected = gdf.to_crs("EPSG:3577")

    # Create empty list for results
    distance_results = []

    for i, geom in enumerate(gdf_projected.geometry):

        distances = gdf_projected.distance(geom)

        distances.iloc[i] = np.inf  # ignore self-distance

        nearest_index = distances.idxmin()
        nearest_distance = distances.min()

        distance_results.append(nearest_distance)

    gdf_projected["Nearest_Distance_m"] = distance_results

    print("\nDistance calculation completed.")
    print(gdf_projected[["Nearest_Distance_m"]].head())

    return gdf_projected

# ------- Create Polygon and Spatial Join --------------------
from shapely.geometry import Polygon

def spatial_join_example(gdf):
    """
    Create example polygon and check which plants fall inside.
    """

    # Create simple polygon (example zone)
    polygon = Polygon([
        (145, -35),
        (150, -35),
        (150, -30),
        (145, -30)
    ])

    zones = gpd.GeoDataFrame(
        {"Zone": ["Example_Zone"],
         "geometry": [polygon]},
        crs="EPSG:3577"
    )

    # Spatial join
    joined = gpd.sjoin(
        gdf,
        zones,
        how="left",
        predicate="within"
    )

    print("\nSpatial Join Completed.")
    print(joined[["Zone"]].head())

    return joined

# ----- Check if inside Polygon (Boolean Method)
def check_inside_polygon(gdf):
    """
    Add boolean column if plant is inside polygon.
    """

    polygon = Polygon([
        (145, -35),
        (150, -35),
        (150, -30),
        (145, -30)
    ])

    gdf["Inside_Polygon"] = gdf.within(polygon)

    print("\nInside polygon check completed.")
    print(gdf[["Inside_Polygon"]].head())

    return gdf

# ----- Buffer Zone ----
def create_buffer_zone(gdf, buffer_km=50):
    """
    Create buffer around each plant.
    """

    gdf_projected = gdf.to_crs("EPSG:3577")

    # Convert km to meters
    buffer_meters = buffer_km * 1000

    gdf_projected["Buffer"] = gdf_projected.geometry.buffer(buffer_meters)

    print(f"\n{buffer_km} km buffer created.")

    return gdf_projected

# ------------ Plot Buffer--------------
def plot_buffer(gdf_projected):

    ax = gdf_projected.plot(alpha=0.5)
    gdf_projected["Buffer"].plot(ax=ax, alpha=0.3)

    plt.title("Plant Buffers")
    plt.show()