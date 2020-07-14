#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 20:22:51 2020

@author: riku
"""

#imports
#import itertools
import yfinance as yf 
import matplotlib.pyplot as plt
import matplotlib
#import matplotlib.font_manager as font_manager
matplotlib.use("TkAgg")
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
#from tkinter import filedialog
import pandas as pd
from sys import platform
#import os
#import fnmatch
import json
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

ver = '1.0.3'

# Searchlist class
# bundle the listbox and searchbox together
class Searchlist:
        
    def __init__(self, name, selectmode, immortal=False, statebox=False):
        self.name = name
        #make frame
        self.frame = tk.Frame(f2)
        self.frame.pack(side='left', padx=(2,2))
        #make inner frame for label and 'X' buton
        self.labelframe = tk.Frame(self.frame)
        self.labelframe.pack(side='top')
        #make label
        self.label = tk.Label(self.labelframe, text=self.name, font=myFont)
        self.label.pack(side='left')
        #make 'X' button, though this can be ignored if immortal set to True
        if not immortal:
            self.xbutton=tk.Button(self.labelframe, text="X", font=myFont, fg="red", 
                                   command= lambda: self.remove_stock())
            self.xbutton.pack(side='left')
        #make lbox
        self.lbox = tk.Listbox(self.frame, width=listBoxWid, height=listBoxHt, 
                               selectmode=selectmode, exportselection=False, font=myFont)
        self.lbox.pack(side='top')
        self.lbox.bind('<<ListboxSelect>>', lambda onclick: self.update_searchbox())
        #make inner frame for searchbox and select button
        self.searchframe = tk.Frame(self.frame)
        self.searchframe.pack(side='top')
        #make searchbox
        self.sbox = tk.Entry(self.searchframe, width=5, font=myFont)
        self.sbox.pack(side='left')
        self.sbox.bind("<Return>", lambda keypress: self.run_searchbox())
        if statebox:
                select_button=tk.Button(self.searchframe, text="Select", font=myFont, 
                                        command= lambda: select_state(self.lbox))
                select_button.pack(side='bottom')   
            
    def organize(self):
        #takes the contents of a listbox
        #orders them and removes all unique values
        temp = sorted(list(set(self.lbox.get(0, 'end'))))
        self.lbox.delete(0, 'end')
        for item in temp:
            self.lbox.insert('end', item)

    def populate_listbox(self, lst):
        n = 0
        self.lbox.delete(0,'end')
        for elem in lst:
            self.lbox.insert(n, elem)
            n = n+1
        self.organize() 
        
    def selectall(self):
        self.lbox.select_set(0, 'end')
        
    def remove_stock(self):
        global stock_data
        self.frame.destroy()
        #clear out rows that contain that stock from the stock_data df
        stock_data = stock_data[stock_data.Ticker != self.name]
        print(stock_data.info())
        
    #method to read from the searchbox and select
    #matching items in the corresponding listbox
    def run_searchbox(self):
        element = self.sbox.get()
        if element == "all" or element == "*":
            self.selectall()
        elif ":" in element:
            self.rangeselect(element)
        else:
            self.lbox.selection_clear(0, 'end')
            element = element.split()
            for curElemVal in element:
                index = self.search_lbox_index(curElemVal)
                self.lbox.select_set(index)
                
    def search_lbox_index(self, element):
        try:
            index = list(self.lbox.get(0, 'end')).index(element)
        except ValueError: 
            try:
                index = list(self.lbox.get(0, 'end')).index(int(element))
            except ValueError:
                try:
                    index = list(self.lbox.get(0, 'end')).index(float(element))
                except ValueError:
                    index = -1
                    print("Unavailable list value entered in searchbox")
        return index
    
    def rangeselect(self, element):
        selection = element.split(":")
        start = selection[0]
        end = selection[1]
        self.lbox.selection_clear(0, 'end')
        start_index = self.search_lbox_index(start)
        end_index = self.search_lbox_index(end)
        self.lbox.select_set(start_index, end_index)
        self.lbox.see(start_index)
    
    #method to put listbox values into 
    #corresponding entrybox
    def update_searchbox(self):
        self.sbox.delete(0, 'end')
        lbox_selected_vals = read_listbox(self.lbox)
        if len(lbox_selected_vals) == self.lbox.size():
            self.sbox.insert(0, '*')
        else:
            self.sbox.insert(0, lbox_selected_vals)

#functions

#read config file, return it as a dict
def read_config():
    try:
        with open('./config/config.json') as config_file:
            data = json.load(config_file)
    except:
        print("ERROR: config file not found")
    return data

#get toplevel data from config
def get_from_config(key):
    data = read_config()
    return data.get(key,"ERROR: Value not found")
    
def load_from_config():
    global listchain
    #clear pre-existing listchain if any
    clear_listchain()
    #when load from config button is pressed, start from here
    data = read_config()
    statelist_key = "states" #all the states are listed under this key
    statenames = sorted(data[statelist_key].keys())
    #make a searchlist, with statebox specific code, to contain all the states
    state_select = Searchlist("Select State", 'browse', statebox=True)
    state_select.populate_listbox(statenames)

#once a state is selected, get the tickerlist stored in that state
#and create a listchain using that list
def select_state(statebox):
    global preset_vals
    data = read_config()
    #all states are listed under this key
    statelist_key = "states"
    #get the specifc state the user selected as a list
    state = read_listbox(statebox)
    #under each specific state the ticker list is listed under this key
    tickerlist_key = "stock_tickers"
    #given all three keys get the actual list
    tickerlist = data[statelist_key][state[0]].get(tickerlist_key)
    #get preset vals now also
    preset_vals_key = "preset_vals"
    preset_vals = data[statelist_key][state[0]].get(preset_vals_key)
    #put the tickerlist into the searchbox and pull stock data
    ent_browse.delete(0, 'end')
    ent_browse.insert(0, tickerlist)
    pull_stock_data()
    
def load_preset_vals():
    #given preset values, put them into their corresponding listchainlinks
    #with the double for loop strategy you dont even need to have your 
    #config json in the same order as your tickerlist
    for key in preset_vals:
        temp = preset_vals.get(key)
        for link in listchain:
            if str(link.name) == str(key):
                link.sbox.insert(0, temp)
                link.run_searchbox()
                break
        
def get_unique(column, data):
     return data[column].unique().tolist()

def read_listbox(lbox):
    sel = []
    for index in lbox.curselection():
        sel.append(lbox.get(index))
    return sel

def clear_listchain():
    global stock_data
    # destroy all widgets from frame
    for widget in f2.winfo_children():
       widget.destroy()
    
### the "big three" functions below.
# 1. pull data
# 2. make a listchain
# 3. plot the data

# this function takes ticker name(s) as input
# pulls data from yahoo
# and returns it as a pandas dataframe
def pull_stock_data():
    #setup global variables
    global stock_data
    global stock_cols
    #reset stock_data to empty
    stock_cols = []
    stock_data = pd.DataFrame()
    #setup local variables
    startdate = get_from_config("start_date")
    enddate = get_from_config("end_date")
    #handle user input
    userinput = ent_browse.get()
    tickerlist = userinput.split(",")
    for ticker in tickerlist:
        ticker = ticker.strip() #remove whitespace from front and back of ticker
        #set a unique filepath for that ticker
        filepath = './stock_data/{}_{}_{}.csv'.format(ticker, startdate, enddate)
        #get stock data using yahoo finance api
        data = yf.download(ticker, startdate, enddate)
        #save that stockdata to its unique path
        data.to_csv(filepath)
        #read it back as a dataframe
        temp = pd.read_csv(filepath)
        #add a pk column
        temp['Ticker'] = ticker
        #append into stock_data, which will contain data for entire tickerlist
        stock_data = stock_data.append(temp)
        stock_cols = list(data.columns)
    #once dataframe is made, create and populate the listchain
    #push dataframe metadata to log window
    print(stock_data.info())
    create_listchain(stock_data)
    
def create_listchain(df):
    global listchain
    #clear pre-existing listchain if any
    clear_listchain()
    listchain_names = ['Date Range']
    list_of_stocks = get_unique('Ticker', df)
    for stock in list_of_stocks:
        listchain_names.append(stock)
    first = True #this lets us handle the Date Listbox independent of the others
    chainlength = len(listchain_names)
    chainlink = 0
    listchain = []
    for link in range(chainlength):
        if first:
            link = Searchlist(listchain_names[chainlink], 'extended', immortal=True)
            listchain.append(link)
            link.populate_listbox(list(df['Date']))
            first = False
        else:
            link = Searchlist(listchain_names[chainlink], 'multiple')
            listchain.append(link)
            link.populate_listbox(stock_cols)
        chainlink = chainlink + 1
    #load preset values
    load_preset_vals()
            
def stockplot():
    fig, ax = plt.subplots(ncols=1, figsize=(8.25,3.7), dpi=100)
    x = []
    y = []
    #actual plot code
    #x-axis is always going to be time.
    x_axes = 'Date'
    #mask dataframe by the dates in the date range
    date_range = (read_listbox(listchain[0].lbox))
    mask = stock_data[x_axes].isin(date_range)
    masked_data = stock_data[mask]
    #y-axis has to plot each user selection for each stock individually
    list_of_stocks = get_unique('Ticker', stock_data)
    chainlink = 1
    for stock in list_of_stocks:
        y_axes = read_listbox(listchain[chainlink].lbox)
        x = masked_data.loc[masked_data['Ticker'] == stock, x_axes]
        chainlink = chainlink + 1
        for elem in y_axes:
            #y = stock_data[elem]
            y = masked_data.loc[masked_data['Ticker'] == stock, elem]
            #check if log scale is desired for either axis
            if y_log.get():
                plt.yscale('log')
            if x_log.get():
                plt.xscale('log')
            ax.plot(x, y, '-o', lw=0.25, markersize=2)

    #plot design code
    ax.set_xticklabels([])

    fig.subplots_adjust(left=0.075, right=0.6)

    ax.grid(linestyle='--', color='lightgray')
    ax.set_xlabel(x_axes, color='b')
    ax.set_ylabel(y_axes[0], color='b')
    
    #frame 3 contains the graph    
    graph_frame = tk.Frame(f3)
    graph_frame.grid(row=0, column=0, columnspan=7, sticky='W')
    
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, graph_frame)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            
#creates popup when closing out of the interface
def callback():
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            window.quit()

#main/layout

global window

window = tk.Tk()
if platform == "win32":
    window.protocol("WM_DELETE_WINDOW", callback)
myFont = tkfont.Font(family="Calibri", size=8, weight="normal")
z_len = myFont.measure("0")
scrnWid = window.winfo_screenwidth()
scrnFrac = 0.6
numListBoxes = 10
listBoxWid = int(scrnWid * scrnFrac / numListBoxes / z_len)
listBoxHt = 5
listBoxPadx = int(listBoxWid/5)
listBoxPady = int(listBoxWid/5)

#### three frame structure:
#frame 1 contains the browse and load buttons
f1 = tk.Frame(window)
f1.master.title('stockViz ver ' + ver)
f1.pack(side='top')
#frame 2 contains the listbox chain
global f2
f2 = tk.Frame(window)
f2.pack(side='top')
#frame 3 contains the graph
global f3
f3 = tk.Frame(window)
f3.pack(side='top')

#### frame 1 stuff here:

#frame 1, column order
ent_browse_col = 0
 #column 1 is skipped because ent_browse has columnspan = 2
load_button_col = 2
load_from_config_button_col = 3
reset_button_col = 4
frame_log_options_col = 5
plot_button_col = 6

# entry box for ticker names
ent_browse=tk.Entry(f1, font=myFont)
ent_browse.grid(row=0, column=ent_browse_col, columnspan=2, sticky='EW', padx=(listBoxPadx,listBoxPadx))
ent_browse.bind("<Return>", lambda keypress: pull_stock_data())

# load button to pull stock data from yahoo
load_button=tk.Button(f1, text="Load", font=myFont, command= lambda: pull_stock_data())
load_button.grid(row=0, column=load_button_col, padx=(2,2))

# load button to pull stock data from stocks that are listed 
# in the the config file, instead of by user input
load_from_config_button=tk.Button(f1, text="Load Config", font=myFont, command= lambda: load_from_config())
load_from_config_button.grid(row=0, column=load_from_config_button_col, padx=(2,2))

# plot button
plot_button=tk.Button(f1, text="Plot", font=myFont, command= lambda: stockplot())
plot_button.grid(row=0, column=plot_button_col, padx=(2,2))

# reset button
reset_button=tk.Button(f1, text="Reset", font=myFont, command= lambda: clear_listchain())
reset_button.grid(row=0, column=reset_button_col, padx=(2,2))

#frame_log_options contains the log scale options
frame_log_options = tk.Frame(f1)
frame_log_options.grid(row=0, column=frame_log_options_col)
#label for log scale checkboxes
loglabel = tk.Label(frame_log_options, text="Use log scale:", font=myFont)
loglabel.pack(side='top')
#checkbox to change y-axis to log scale
y_log = tk.IntVar()
cb1 = tk.Checkbutton(frame_log_options, text="y-axis", font=myFont, variable=y_log)
cb1.pack(side='top')
#checkbox to change x-axis to log scale
x_log = tk.IntVar()
cb2 = tk.Checkbutton(frame_log_options, text="x-axis", font=myFont, variable=x_log)
cb2.pack(side='top')

#### frame 2 stuff here:
 ## frame 2 contents are generated in the create_listchain() function
#### frame 3 stuff here:
 ## frame 3 contents are generated in the stockplot() fuction

window.mainloop()