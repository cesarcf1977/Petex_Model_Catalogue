# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 14:12:17 2024

@author: Cesar Correa Feria
"""
#prosper_mc.py

#%% Import required modules
import petexosfunctions as pos
import prospermcfunctions as pmc
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

#%% TESTS: perform a complete lifecycle model management workflow.
pos.connect()

# PROSPER SHOULD BE OPEN
# pos.docmd('PROSPER.START()')

# Open model
pos.docmd(f'PROSPER.OPENFILE({modelPath})')

if mode == 'Test': # Runs through all functionalities
    # Step 1: Read OS variables from Prosper
    test = pmc.readOsProsper (osVarFile, filter)
    
    # Step 2: Store values in database: create or update
    pmc.writeSQL(test, dbPath, wellName, columnName)
    
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
        pmc.writeSQL(test, dbPath, wellName, columnName)
    
    # Step 4: Retrieve and plot model history
    presData = pmc.plotData(dbPath, wellName, osSample1, key)
    piData = pmc.plotData(dbPath, wellName, osSample2, key)
    wcData = pmc.plotData(dbPath, wellName, osSample3, key)

    fig, ax1 = plt.subplots()
    fig.suptitle("Test Model")
    ax2 = ax1.twinx()
    ax1.plot(presData, color='red', label='Reservoir pressure')
    ax1.legend(loc=2)
    ax2.plot(piData, color='orange', label='Productivity index')
    ax2.plot(wcData, color='blue', label='Water cut')
    ax2.legend(loc=4)

    # Step 5: Read from database and update Prosper to a previous state
    input = pmc.readSql(dbPath, wellName, testColumnName)
    pmc.writeOsProsper(input)

elif mode == "Real": # Reads current state for all models in a folder. History init.
    path = os.path.abspath(r'.\models')
    dir = os.listdir( path )
    for file in dir:
        if os.path.splitext(file.upper())[1] == '.OUT':
            print(file)
            # Open model
            modelPath = path + '\\' + file
            pos.docmd(f'PROSPER.OPENFILE({modelPath})')
            test = pmc.readOsProsper (osVarFile, filter)
            wellName = os.path.splitext(file.upper())[0]
            columnName = 'Update_' + datetime.now().strftime('%Y%m%d_%H%M%S%p')
            pmc.writeSQL(test, dbPath, wellName, columnName)

pos.disconnect()