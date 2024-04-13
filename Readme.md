## DESCRIPTION
This script allows you to implement a simple, but fully functional, version control workflow for Petroleum Experts PROSPER models. It is easily extensible to any other IPM model that communicates through OpenServer.

If you are familiar with Model Catalogue, this performs a tiny -but core- piece of its many functionalities, retrieving all or only key model information and storing it timestamped in a database.

This aims to assist engineers in keeping a register of all model changes without the hassle of having to do it manually or, the most usual outcome, not doing it at all.

## CONTENTS

**prosper_mc.py**: Main script; all code is centralized here except the OpenServer functions.

**petexosfunctions\.py**: OpenServer functions (doGet, doSet, doCmd, etc).

**model_history.sqlite**: Database file resulting from running the script.

**Prosper_OS_Variables.txt**: All Prosper OpenServer strings (variables).

**Prosper_OS_Variables_main.txt**: Group of handpicked Openserver strings.

**models folder**: Constains a few sample Prosper models (from IPM samples).

**output.png**: Dummy model history sample.

## INSTRUCTIONS
If you want to run a quick test of all functionalities from scratch, just delete the database file, open any Prosper model, and run the main script in 'Test' mode.

If you want to use it for more serius business, you'll have to create something for your specific application. Usually it would involve at least a loop through all Prosper files in a specific folder, reading all or just the required OpenSever variables from them, and storing the values in the database as your initial models status. Then run that same functions periodically to capture model changes and thus creating history. This is quickly done using 'Real' mode.


## DISCLAIMERS
Plenty to optimize on the database management and queries, but this is just a working example...and works.

In this mvp, everything is treated and stored as text in the database. You can keep it like that and perform the required conversions when reading the data, or implement custom types as required.