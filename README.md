Project Title: AEMO Generation Tracker 

This project uses Python to process and analyse 2026 electricity generation data published by the Australian Energy Market Operator (AEMO). For relational analysis, 2025 and 2026 AEMO data is used in SQL.  
The objective is to transform raw generator data into a structured, validated, and analysis-ready database for energy market intelligence.

Project Objective: 
•	Load, convert (excel to csv) and clean raw generation dataset
•	Remove duplicate records
•	Standardise formats (dates, capacity, text fields)
•	Handle null and unknown values correctly
•	Validate data integrity
•	Filter currently operating sites
•	Generate regional and technology-level capacity summaries
•	Produce reporting-ready outputs
•	MySQL to Python connection to access SQL database
•	GeoJSON export of project (fake data)

Getting Started: 
Install Pycharm and MySQL Workbench to run Python scripts respectively. Install following libraries to run the  scripts – 
•	Openpyxl for reading, writing, and modifying Excel files (which have the .xlsx or .xlsm extensions)
•	Pandas, Pathlib, Matplotlib, Numpy
•	Geopandas, Shapely.geometry for geospatial 
•	Datetime
•	SQL – connector – Python

Output: 
Image of Geospatial project, Image of capacity by region, Operating plants Geojson
Screenshots of SQL database design, SQL query sample
