# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 14:12:17 2016

@author: Cesar Correa Feria
"""
#petexosfunctions.py

import win32com.client as win32
import ctypes  # An included library with Python install.
import sys

def connect():
    """This utility creates the OpenServer object which allows comunication between Excel and IPM tools"""
    global connected, server
    try: 
        connected
    except NameError:
        server = win32.Dispatch('PX32.OpenServer.1')
        connected = 1  
    else:
        connected = 0
     
def disconnect():
    """This utility destroys the OpenServer object which allows comunication between Excel and IPM tools"""  
    global connected, server
    if connected == 1:
        server = None
        connected = 0

def getappname(strval):
    """This utility function extracts the application name from the tag string"""
    pos = strval.find(".")
    if pos < 2:
        ctypes.windll.user32.MessageBoxW(0, "Badly formed tag string", "OpenServer Error", 1) 
        disconnect()
        sys.exit(0)
    getappname = strval[:pos]
    applist = ["PROSPER", "MBAL", "GAP", "PVT"]
    if getappname not in applist:
        ctypes.windll.user32.MessageBoxW(0, "Unrecognised application name in tag string", "OpenServer Error", 1)
        disconnect()
        sys.exit(0)
    return getappname
        
def docmd(cmd):    
    """Perform a command, then check for errors"""
    lerr = server.DoCommand(cmd)
    if lerr > 0:
        ctypes.windll.user32.MessageBoxW(0, server.GetErrorDescription(lerr), "OpenServer Error", 1)
        disconnect()

def doset(sv, val, error_msgbox=True):
    """Set a value, then check for errors"""
    global server
    lerr = server.SetValue(sv, val)
    appname = getappname(sv)
    lerr = server.GetLastError(appname)
    if lerr > 0:
        if error_msgbox:
            ctypes.windll.user32.MessageBoxW(0, server.GetErrorDescription(lerr), "OpenServer Error", 1)
            disconnect()
 
def doget(gv, return_float = True, return_round = 2, error_msgbox=True):
    """Get a value, then check for errors"""
    """Returns a 2 decimal float by default, string otherwise"""
    doget = server.GetValue(gv)
    appname = getappname(gv)
    lerr = server.GetLastError(appname)
    if lerr > 0:
        if error_msgbox:
            ctypes.windll.user32.MessageBoxW(0, server.GetLastErrorMessage(appname), "OpenServer Error", 1)
            disconnect()
    if return_float:
        return round(float(doget), return_round)
    else:
        return doget
    
def doslowcmd(cmd):
    """Perform a command, then wait for the command to exit. Then check for errors"""
    step = 0.001
    appname = getappname(cmd)
    lerr = server.DoCommandAsync(cmd)
    if lerr > 0:
        ctypes.windll.user32.MessageBoxW(0, server.GetErrorDescription(lerr), "OpenServer Error", 1)
        disconnect()
        sys.exit(0)
    while server.IsBusy(appname) > 0:
        if step < 2:
            step = step * 2
    appname = getappname(cmd)
    lerr = server.getlasterror(appname)
    if lerr > 0:
        ctypes.windll.user32.MessageBoxW(0, server.GetErrorDescription(lerr), "OpenServer Error", 1)
        disconnect()
        sys.exit(0)

def dogapfunc(gv):
    doslowcmd(gv)
    dogapfunc = doget("GAP.LASTCMDRET") 
    lerr = server.GetLastError("GAP")
    if lerr > 0:
        ctypes.windll.user32.MessageBoxW(0, server.GetErrorDescription(lerr), "OpenServer Error", 1)
        disconnect()
        sys.exit(0)

def getlasterror(appname):
    return server.GetLastError(appname)
    