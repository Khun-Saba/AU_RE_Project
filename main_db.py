import aemo_database as adb
from datetime import date

def publish_results(p):
    for i in p:
        print(i)

g25 = adb.access_g25()
publish_results(g25)

inner_j = adb.access_inner_join()
publish_results(inner_j)