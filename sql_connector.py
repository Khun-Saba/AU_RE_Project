import mysql.connector #install mysql drive for each project from "settings" of PyCharm


mydb = mysql.connector.connect(
    host = "localhost",
    user = "<user name>",
    password = "<password>",
    database = "aemo_generation"
)

mycursor = mydb.cursor()

def my_query(query):
    mycursor.execute(query)
    initial_results = mycursor.fetchall()
    return initial_results




