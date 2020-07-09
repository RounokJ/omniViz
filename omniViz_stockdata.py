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
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

ver = '1.0.0'

# Searchlist class
# bundle the listbox and searchbox together
class Searchlist:
        
    def __init__(self, name):
        self.name = name
        self.frame = name + "frame"
        self.label = name + "label"
        self.lbox = name + "lbox"
        self.sbox = name + "sbox"
            
    def make_searchlist(self, selectmode):
        #make frame
        self.frame = tk.Frame(f2)
        self.frame.pack(side='left', padx=(2,2))
        #make label
        self.label = tk.Label(self.frame, text=self.name, font=myFont)
        self.label.pack(side='top')
        #make lbox
        self.lbox = tk.Listbox(self.frame, width=listBoxWid, height=listBoxHt, 
                               selectmode=selectmode, exportselection=False, font=myFont)
        self.lbox.pack(side='top')
        self.lbox.bind('<<ListboxSelect>>', lambda onclick: self.update_searchbox())
        #make searchbox
        self.sbox = tk.Entry(self.frame, width=5, font=myFont)
        self.sbox.pack(side='top')
        self.sbox.bind("<Return>", lambda keypress: self.run_searchbox())
        
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

# this function takes ticker name(s) as input
# pulls data from yahoo
# and returns it as a pandas dataframe
def pull_stock_data():
    #setup global variables
    global stock_data
    global stock_cols
    stock_cols = []
    stock_data = pd.DataFrame()
    #setup local variables
    startdate = '2018-01-01'
    enddate = '2020-01-01'
    #handle user input
    userinput = ent_browse.get()
    tickerlist = userinput.split(",")
    for ticker in tickerlist:
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
    
def get_unique(column, data):
     return data[column].unique().tolist()

def read_listbox(lbox):
    sel = []
    for index in lbox.curselection():
        sel.append(lbox.get(index))
    return sel

def create_listchain(df):
    global listchain
    listchain_names = ['Date Range']
    list_of_stocks = get_unique('Ticker', df)
    for stock in list_of_stocks:
        listchain_names.append(stock)
    first = True #this lets us handle the Date Listbox independent of the others
    chainlength = len(listchain_names)
    chainlink = 0
    listchain = []
    for link in range(chainlength):
        link = Searchlist(listchain_names[chainlink])
        listchain.append(link)
        if first:
            link.make_searchlist('extended')
            link.populate_listbox(list(df['Date']))
            first = False
        else:
            link.make_searchlist('multiple')
            link.populate_listbox(stock_cols)
        chainlink = chainlink + 1
            
def stockplot():
    fig, ax = plt.subplots(ncols=1, figsize=(8.25,3.7), dpi=100)
    
    x = []
    y = []
    
    #actual plot code
    #x-axis is always going to be time.
    x_axes = 'Date'
    #y-axis has to plot each user selection for each stock individually
    list_of_stocks = get_unique('Ticker', stock_data)
    chainlink = 1
    for stock in list_of_stocks:
        y_axes = read_listbox(listchain[chainlink].lbox)
        x = stock_data.loc[stock_data['Ticker'] == stock, x_axes]
        chainlink = chainlink + 1
        for elem in y_axes:
            #y = stock_data[elem]
            y = stock_data.loc[stock_data['Ticker'] == stock, elem]
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
# entry box for ticker names
ent_browse=tk.Entry(f1, font=myFont)
ent_browse.grid(row=0, column=0, columnspan=2, sticky='EW', padx=(listBoxPadx,listBoxPadx))
ent_browse.bind("<Return>", lambda keypress: pull_stock_data())

# load button to pull stock data from yahoo
load_button=tk.Button(f1, text="Load", font=myFont, command= lambda: pull_stock_data())
load_button.grid(row=0, column=3, padx=(2,2))

# plot button
plot_button=tk.Button(f1, text="Plot", font=myFont, command= lambda: stockplot())
plot_button.grid(row=0, column=4, padx=(2,2))

#### frame 2 stuff here:
 ## frame 2 is generated in the create_listchain() function
#### frame 3 stuff here:

window.mainloop()