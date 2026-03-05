USE aemo_generation;
SELECT* FROM generation_2025_12 LIMIT 10;
SELECT* FROM generation_2026_1 LIMIT 10;
DESCRIBE generation_2025_12;

------ Clean and format data --------------
SELECT last_updated, STR_TO_DATE(last_updated, '%d-%b-%y') AS converted FROM generation_2025_12 LIMIT 5;
SET SQL_SAFE_UPDATES = 0;
UPDATE generation_2025_12 
SET last_updated = STR_TO_DATE(last_updated, '%d-%b-%y');

-- Count duplicate DUID ----
SELECT DUID, COUNT(DUID) AS count FROM generation_2025_12 GROUP BY DUID having count > 1;

SELECT* FROM generation_2025_12 WHERE duid IS NULL OR TRIM(duid) = '';
DELETE FROM generation_2025_12 WHERE duid IS NULL OR TRIM(duid) = '';
-- Select why DUID has duplicates
SELECT * FROM generation_2025_12 WHERE duid = 'AGLHAL';
-- Delete duplicates - self-join delete keeping the lowest surrogate key
DELETE t1
FROM generation_2025_12 t1
JOIN generation_2025_12 t2
ON t1.duid = t2.duid
AND t1.id > t2.id;

------- validate both table for specific region ------
select* from generation_2025_12 where duid in (select duid from generation_2026_1 where region = 'QLD1');

----- capacity by region and technology ---- 
select region, sum(Unit_Capacity_MW) from generation_2026_1 group by region;
select Technology_Type, avg(Unit_Capacity_MW) from generation_2026_1 where region = 'NSW1' group by Technology_Type;
select Technology_Type, avg(Unit_Capacity_MW) from generation_2026_1 group by Technology_Type;

-- join tables  to compare both tables ---- 
select*
from generation_2025_12 as g25
inner join generation_2026_1 as g26
    on g25.duid = g26.duid
where g26.region = 'QLD1';

select* from generation_2025_12 as g25 
	left join generation_2026_1 as g26
	on g25.duid = g26.duid
	where g26.technology_type = 'Solar PV';

---- Preveiw for reporting
create view total_capacity_by_region as
 select region, sum(Unit_Capacity_MW) from generation_2026_1 group by region;
 select* from total_capacity_by_region;
    
    


 


