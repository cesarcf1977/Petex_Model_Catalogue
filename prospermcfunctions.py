# -*- coding: utf-8 -*-
"""
Created on Tue Apr  12 16:22:03 2024

@author: Cesar Correa Feria
"""
#prospermcfunctions.py

#%% Import required modules
import pandas as pd
import petexosfunctions as pos
import sqlite3 as sql
import os

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

def plotData(dbPath, tableName, osVar, key):
    """Function managing querying and data conversion for plotting the history of numerical variables.

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

