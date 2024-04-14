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
filter = ['.PVT', '.SIN', '.COR'] # Any OpenServer string containing these will be executed. To include everything, just list 'PROSPER'.
wellName = 'Well01' # Each well history will be kept in a separate SQL table. This will be the name of the table.
columnName = 'Update_' + datetime.now().strftime('%Y%m%d_%H%M%S%p') # Each new column added to the well table will be named as "Update_timestamp".
key = 'osString' # Column used to store the OpenServer strings. Should be UNIQUE.
mode = 'Test' # Debugging purposes.

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
    
    # Step 3: Update models (will use a loop to randomly generate 50 dummies here)
    testColumnName = columnName # Keep first column name to write values to Prosper later. Just for testing; you could define which state you want to return the model to.
    osSample1, osSample2, osSample3, osSample4, osSample5 = ['PROSPER.SIN.IPR.SINGLE.PRES', 'PROSPER.SIN.IPR.SINGLE.PINDEX', 'PROSPER.SIN.IPR.SINGLE.WC', 
    'PROSPER.ANL.COR.CORR[{PETROLEUMEXPERTS2}].A[0]', 'PROSPER.ANL.COR.CORR[{PETROLEUMEXPERTS2}].A[1]']
    for i in range(50):
        time.sleep(1) # Pause at least 1 second so columName changes
        for name in [osSample1, osSample2, osSample3, osSample4, osSample5]:
            test.loc[test['osString'] == name, 'osValue'] = str(float(test.loc[test['osString'] == name, 'osValue'].iloc[0])*randint(95,105)/100)

        columnName = 'Update_' + datetime.now().strftime('%Y%m%d_%H%M%S%p')
        pmc.writeSQL(test, dbPath, wellName, columnName)
    
    # Step 4: Retrieve and plot model history 
    presData, piData, wcData, p1Data, p2Data = [pmc.plotData(dbPath, wellName, x, key) for x in [osSample1, osSample2, osSample3, osSample4, osSample5]]

    fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(9,6))
    fig.suptitle("Test Model History")
    fig.supxlabel('Model update #')
    ax[0].set_ylabel('Pressure')
    ax[1].set_ylabel('PI, WC')
    ax[2].set_ylabel('P1, P2')
    ax[0].plot(presData, color='red', label='Reservoir pressure')
    ax[0].legend(loc=1)
    ax[1].plot(piData, color='orange', label='Productivity index')
    ax[1].plot(wcData, color='blue', label='Water cut')
    ax[1].legend(loc=2, ncol=2)
    ax[2].plot(p1Data, color='black', label='Corr P1')
    ax[2].plot(p2Data, color='green', label='Corr P2')
    ax[2].axhline(0.9, color='red', linestyle='dashed')
    ax[2].axhline(1.1, color='red', linestyle='dashed')
    ax[2].legend(loc=2)
    
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