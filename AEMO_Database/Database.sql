CREATE TABLE generation_2025_12 (
    site_name VARCHAR(150),
    duid VARCHAR(50),
    expected_closure_year YEAR,
    closure_date VARCHAR(20),
    last_updated VARCHAR(20)
);

ALTER TABLE generation_2025_12
ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE generation_2025_12
DROP COLUMN closure_date;

CREATE TABLE generation_2026_1(
	id INT auto_increment primary key,
    duid VARCHAR(50),
    Site_Name VARCHAR(150),
	Region VARCHAR (50),
    Technology_Type VARCHAR (100),
	Dispatch_Type VARCHAR (50),
	Unit_Capacity_MW decimal (10,2),
	Commitment_Status VARCHAR (100), 	
    Full_Commercial_Use YEAR
    );
    
ALTER TABLE generation_2026_1 MODIFY COLUMN Unit_Capacity_MW INT;

