import sql_connector
from datetime import date

# ----- access generation_2025_12 table
def access_g25():
    final_results= sql_connector.my_query('Select* from generation_2025_12')
    return final_results

# ----- -- Inner join tables -----
def access_inner_join():
    final_results = sql_connector.my_query('select* from generation_2025_12 as g25 inner join generation_2026_1 as g26 on g25.duid = g26.duid where g26.region = "QLD1"')
    return final_results
