## DESCRIPTION
This script allows you to implement a simple, but fully functional, version control workflow for Petroleum Experts PROSPER models. It is easily extensible to any other IPM model that communicates through OpenServer.

If you are familiar with Model Catalogue, this performs a tiny -but core- piece of its many functionalities, retrieving all or only key model information and storing it timestamped in a database.

This aims to assist engineers in keeping a register of all model changes without the hassle of having to do it manually or, the most usual outcome, not doing it at all.

## CONTENTS

**prospermc\.py**: Main script; runs trough all functionalities over a few sample models.

**prospermcfunctions\.py**: For clarity, all developed functions to manage OpenServer and Database operations are stored in a dedicated file.

**petexosfunctions\.py**: OpenServer functions (doGet, doSet, doCmd, etc).

**model_history.sqlite**: Database file resulting from running the script.

**Prosper_OS_Variables.txt**: All Prosper OpenServer strings (variables).

**Prosper_OS_Variables_main.txt**: Group of handpicked Openserver strings.

**models folder**: Constains a few sample Prosper models (from IPM samples).

**output.png**: Dummy model history sample.

## INSTRUCTIONS
If you want to run a quick test of all functionalities from scratch, just delete the database file, open any Prosper model, and run the main script in 'Test' mode.

If you want to use it for more serius business, you'll have to create something for your specific application. Usually it would involve at least a loop through all Prosper files in a specific folder, reading all or just the required OpenSever variables from them, and storing the values in the database as your initial models status. Then run that same functions periodically to capture model changes and thus creating history. This is quickly done using 'Real' mode.

For managing the database I find using https://sqlitebrowser.org/ quite handy.

## DISCLAIMERS
Plenty to optimize on the database management and queries, but this is just a working example...and works.

In this mvp, everything is treated and stored as text in the database. You can keep it like that and perform the required conversions when reading the data, or implement custom types as required.

## FUTURE WORK
The version control and model data historization is a powerful feature on its own and should be part of any serious well and network modeling practice. Through conventional analysis of that information a lot of disparate and poor modeling practices <ins>will</ins> be identified and, hopefully, fixed.

Looking to do something fancier, however, with a reasonable amount of models history gathered in combination with actual well and reservoir production history, it is entirely possible to propose a ML project that identifies usual modelling practices and performs an automatic model tuning process accordingly.
