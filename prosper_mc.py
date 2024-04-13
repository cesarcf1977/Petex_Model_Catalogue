# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 14:12:17 2024

@author: Cesar Correa Feria
"""
#prosper_mc.py

#%% Import required modules
import pandas as pd
import petexosfunctions as pos
import sqlite3 as sql
import matplotlib.pyplot as plt
import time
import os

from datetime import datetime
from random import randint

#%% Define configuration parameters

osVarFile = "Prosper_OS_Variables_main.txt" # Path/name for the text file containing OpenServer strings. All strings can be exported from Prosper.
dbPath = r'.\model_history.sqlite' # Path/name where the SQLite databse is stored or will be created
modelPath = os.path.abspath(r'.\models\well_A.Out') # Full model path. OS is not getting paths relative to .py but Prosper.exe
filter = ['.PVT', '.SIN'] # Any OpenServer string containing these will be executed. To include everything, just list 'PROSPER'.
wellName = 'Well01' # Each well history will be kept in a separate SQL table. This will be the name of the table.
columnName = 'Update_' + datetime.now().strftime('%Y%m%d_%H%M%S%p') # Each new column added to the well table will be named as "Update_timestamp".
key = 'osString' # Column used to store the OpenServer strings. Should be UNIQUE.
mode = 'Real' # Debugging purposes.


#%% Function definitions

def readOsProsper (osVarFile, filter): 
    """Function that reads an input file containing OpenServer strings
    and gets the values from Prosper.
    
        osVarFile:  text file containing OpenServer variable strings
        filter:     list containing substrings acting as filter. 
                    If there is a match between the OpenServer string and the filter, 
                    the OpenServer query will be executed. Ignored otherwise.
    """
    results = []
    filter = [x. upper() for x in filter]  # All work done in uppercase to avoid unintentional mismatches
    with open (osVarFile) as file:
        for line in file:
            line = line.upper() 
            line = line.replace('\n','')
            if any(word in line for word in filter):
                try:
                    result = pos.doget(line, return_float=False, error_msgbox=False)
                    results.append((line, result))
                    print ((line, result)) # Just for debugging purposes. 
                except Exception as e:
                    print (e.args)

            else:
                results.append((line, "Filtered out"))

    results = pd.DataFrame(results, columns=['osString', 'osValue'])

    return results

def writeOsProsper (inputs): # Set values to Prosper
    """Function that writes OpenServer strings and values
    into Prosper.
    
        inputs:  a dataframe containing 2 columns (osString, osValue)
    """
    pos.connect()
    for index, row in inputs.iterrows():
        if row.iloc[1] != 'Filtered out': # Ignore elements that were not read from Prosper. 
            try:
                pos.doset(row.iloc[0].upper(), row.iloc[1], error_msgbox=False)
                print (row.iloc[0], row.iloc[1])
            except Exception as e:
                print (e.args)
    pos.disconnect()

    return

def writeSQL(df, dbPath, tableName, columnName, key = 'osString'):
    """Not-so-simple function that manages all the writing to the SQLite
    database.

        df: a dataframe containing 2 columns (osString, osValue) to be written to the database
        dbPath: database file path
        tableName: wellName (each well's data is stored in a separate table)
        columnName: some timestamped name that allows future identification of model parameters
        key: name of the column contianing the OpenServer strings
    """
    # Check if database exists
    fileExists = os.path.exists(dbPath)

    # Connect to database
    conn = sql.connect(dbPath) # If DB does not exist, it will be created
    cur = conn.cursor()

    if fileExists: # Update existing database and table with new column
        print("DB exists")
        
        # Check if tableName exists
        try:
            query = f'select * from {tableName} limit 1'
            cur.execute(query)
            names = list(map(lambda x: x[0], cur.description))
        except: # Create table if not
            print (f'Table {tableName} does not exist. Will be created.')
            query = f'CREATE TABLE {tableName} ({key}	TEXT UNIQUE, {columnName}	TEXT)' 
            print(query)
            cur.execute(query)
            names = [columnName]
        #print (names)
        
        if columnName not in names:
            # Add new column
            print (f'Column {columnName} does not exist. Will be created.')
            query = f'ALTER TABLE {tableName} ADD {columnName}'
            cur.execute(query)
            #print (query)
        else:
            print (f'Column {columnName} exists. Will be updated.')
        
        # Bulk insert values (assume values_list contains (time, value) tuples)
        multiInsertSQL(df, tableName, columnName, key, cur)

    else: # Create new database and table
        print("DB does not exist")
        query = f'CREATE TABLE {tableName} ({key}	TEXT UNIQUE, {columnName}	TEXT)' 
        print(query)
        cur.execute(query)
        multiInsertSQL(df, tableName, columnName, key, cur)

    # Commit and close
    conn.commit()
    cur.close()
    conn.close()

def multiInsertSQL(df, tableName, columnName, key, cur):
    """Helper function managing the dataframe iteration for the writeSQL function.

        df: a dataframe containing 2 columns (osString, osValue) to be written to the database
        tableName: wellName (each well's data is stored in a separate table)
        columnName: some timestamped name that allows future identification of model parameters
        key: name of the column contianing the OpenServer strings
        cur: database connection cursor object
    """
    for item in df.iterrows():
        #print (str(item[1].iloc[0]), str(item[1].iloc[1]))
        query = f'INSERT OR IGNORE INTO {tableName} ({key}) VALUES ("{item[1].iloc[0]}")'
        print (query)
        cur.execute(query)
        query = f'UPDATE {tableName} SET {columnName}="{item[1].iloc[1]}" WHERE {key}="{item[1].iloc[0]}"'
        print (query)
        cur.execute(query)

def readSql(dbPath, tableName, columnName, key='osString'):
    """Function managing read operation(s) from the database.

        dbPath: database file path
        tableName: wellName (each well's data is stored in a separate table)
        columnName: some timestamped name that allows future identification of model parameters
        key: name of the column contianing the OpenServer strings
    """
    conn = sql.connect(dbPath) 
    query = f'SELECT {key}, {columnName} FROM {tableName}'
    df = pd.read_sql(query, con=conn)

    return df

def plotData(dbPath, tableName, osVar):
    """Function managing querying, conversion, and plotting the history of numerical variables.

        dbPath: database file path
        tableName: wellName (each well's data is stored in a separate table)
        osVar: OpenServer variable to be plotted
    """
    conn = sql.connect(dbPath) 
    conn.row_factory = lambda cursor, row: row[1:-1]
    cursor = conn.cursor()

    query = f'SELECT * FROM {tableName} WHERE {key}="{osVar}"'
    print (query)
    data = list(sum(cursor.execute(query).fetchall(), ())) # Gibberish to flatten the output...
    data = [float(i) for i in data] # More gibberish to get a list of floats, as everything is stored as strings in this sample.

    return data

#%% TESTS: perform a complete lifecycle model management workflow.
pos.connect()

# PROSPER SHOULD BE OPEN
# pos.docmd('PROSPER.START()')

# Open model
pos.docmd(f'PROSPER.OPENFILE({modelPath})')

if mode == 'Test': # Runs through all functionalities
    # Step 1: Read OS variables from Prosper
    test = readOsProsper (osVarFile, filter)
    
    # Step 2: Store values in database: create or update
    writeSQL(test, dbPath, wellName, columnName)
    
    # Step 3: Update models (will use a loop to randomly generate 20 dummies here)
    testColumnName = columnName # Keep first column name to write values to Prosper later. Just for testing; you could define which state you want to return the model to.
    for i in range(20):
        time.sleep(1) # Pause at least 1 second so columName changes
        osSample1 = 'PROSPER.SIN.IPR.SINGLE.PRES'
        osSample2 = 'PROSPER.SIN.IPR.SINGLE.PINDEX'
        osSample3 = 'PROSPER.SIN.IPR.SINGLE.WC'
        test.loc[test['osString'] == osSample1, 'osValue'] = str(float(test.loc[test['osString'] == osSample1, 'osValue'].iloc[0])*randint(95,101)/100)
        test.loc[test['osString'] == osSample2, 'osValue'] = str(float(test.loc[test['osString'] == osSample2, 'osValue'].iloc[0])*randint(95,105)/100)
        test.loc[test['osString'] == osSample3, 'osValue'] = str(float(test.loc[test['osString'] == osSample3, 'osValue'].iloc[0])*randint(95,105)/100)
        columnName = 'Update_' + datetime.now().strftime('%Y%m%d_%H%M%S%p')
        writeSQL(test, dbPath, wellName, columnName)
    
    # Step 4: Retrieve and plot model history
    presData = plotData(dbPath, wellName, osSample1)
    piData = plotData(dbPath, wellName, osSample2)
    wcData = plotData(dbPath, wellName, osSample3)

    fig, ax1 = plt.subplots()
    fig.suptitle("Test Model")
    ax2 = ax1.twinx()
    ax1.plot(presData, color='red', label='Reservoir pressure')
    ax1.legend(loc=2)
    ax2.plot(piData, color='orange', label='Productivity index')
    ax2.plot(wcData, color='blue', label='Water cut')
    ax2.legend(loc=4)

    # Step 5: Read from database and update Prosper to a previous state
    input = readSql(dbPath, wellName, testColumnName)
    writeOsProsper(input)

elif mode == "Real": # Reads current state for all models in a folder. History init.
    path = os.path.abspath(r'.\models')
    dir = os.listdir( path )
    for file in dir:
        if os.path.splitext(file.upper())[1] == '.OUT':
            print(file)
            # Open model
            modelPath = path + '\\' + file
            pos.docmd(f'PROSPER.OPENFILE({modelPath})')
            test = readOsProsper (osVarFile, filter)
            wellName = os.path.splitext(file.upper())[0]
            columnName = 'Update_' + datetime.now().strftime('%Y%m%d_%H%M%S%p')
            writeSQL(test, dbPath, wellName, columnName)

pos.disconnect()