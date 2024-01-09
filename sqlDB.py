import pandas as pd
from datetime import datetime,timedelta
import pyodbc
import os
from dotenv import load_dotenv
load_dotenv()   # Loading the .env file

try:
    # Connect to MS SQL Server database
    connection_string = (
            'DRIVER=' + os.getenv('driver') + ';'
            'SERVER=' + os.getenv('server') + ';'
            'DATABASE=' + os.getenv('database') + ';'
            'UID=' + os.getenv('username') + ';'
            'PWD=' + os.getenv('password')
    )

    connection = pyodbc.connect(connection_string) # Creating a connection
    cursor = connection.cursor()    # Creating a cursor

    # Function to Fetch all the records from the table
    def fetch_record(id):  
        cursor.execute("SELECT * FROM punchs WHERE id = ?", (id,)) # Fetch all the records
        records = cursor.fetchall()  # Fetch all the records

        # Convert the record to a list and print it
        records = [list(record) for record in records]   # Convert each record to a list
        print("Records:", records)

        return records
    
    # Function to Insert the records in the table
    def insert_record(id):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%d-%m-%Y %H:%M:%S")
        cursor.execute("INSERT INTO punchs (id,time) VALUES (?,?)", (id,formatted_time))
        connection.commit()
        print("Record inserted successfully.")

except pyodbc.Error as e:
    print("Error connecting to the database:", e) # Print error if any
