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
import matplotlib.font_manager as font_manager
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

# Listchain class
# bundle the listbox and searchbox together
class Searchlist:
        
    def __init__(self, name):
        self.name = name
        self.frame = name + "frame"
        self.label = name + "label"
        self.lbox = name + "lbox"
        self.sbox = name + "sbox"
            
    def make_searchbox(self, selectmode):
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
        #make searchbox
        self.sbox = tk.Entry(self.frame, width=5, font=myFont)
        self.sbox.pack(side='top')
        
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

#functions

# this function takes a ticker name as input
# pulls data from yahoo
# and returns it as a pandas dataframe
def pull_stock_data():
    global stock_data
    global stock_cols
    stock_cols = []
    stock_data = pd.DataFrame()
    ticker = ent_browse.get()
    startdate = '2016-01-01'
    enddate = '2018-01-01'
    filepath = './stock_data/{}_{}_{}.csv'.format(ticker, startdate, enddate)
    data = yf.download(ticker, startdate, enddate)
    data.to_csv(filepath)
    temp = pd.read_csv(filepath)
    stock_data = stock_data.append(temp)
    stock_data['Ticker'] = ticker
    stock_cols = list(data.columns)
    #print(stock_data.info())
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
            link.make_searchbox('multiple')
            link.populate_listbox(list(df['Date']))
            first = False
        else:
            link.make_searchbox('browse')
            link.populate_listbox(stock_cols)
        chainlink = chainlink + 1
            
def stockplot():
    fig, ax = plt.subplots(ncols=1, figsize=(8.25,3.7), dpi=100)
    lgndFont = font_manager.FontProperties(family='Calibri', weight='normal', style='normal', size=8)
    axLblFont = font_manager.FontProperties(family='Calibri', weight='bold', style='normal', size=10)
    axFont = font_manager.FontProperties(family='Calibri', weight='normal', style='normal', size=8)
    
    x = []
    y = []
    x_axes = 'Date'
    y_axes = read_listbox(listchain[1].lbox)
    print(y_axes)
    lgnd = "placeholder"
    x = stock_data[x_axes]
    for elem in y_axes:
        y = stock_data[elem]
    ax.plot(x, y, '-o', lw=0.25, markersize=2, label=lgnd)
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontproperties(axFont)
    ax.legend()
    handles, labels = ax.get_legend_handles_labels()
    lgd = dict(zip(labels, handles))
    ax.legend(lgd.values(), lgd.keys(), bbox_to_anchor=(1.04,1), loc="upper left", prop=lgndFont)
    fig.subplots_adjust(left=0.075, right=0.6)

    ax.grid(linestyle='--', color='lightgray')
    ax.set_xlabel(x_axes[0], fontproperties=axLblFont, color='b')
    ax.set_ylabel(y_axes[0], fontproperties=axLblFont, color='b')
    #plt.show()
    
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

# load button to pull stock data from yahoo
load_button=tk.Button(f1, text="Load", font=myFont, command= lambda: pull_stock_data())
load_button.grid(row=0, column=3, padx=(2,2))

# plot button
load_button=tk.Button(f1, text="Plot", font=myFont, command= lambda: stockplot())
load_button.grid(row=0, column=4, padx=(2,2))

#### frame 2 stuff here:
 ## frame 2 is generated in the create_listbox_chain() function
#### frame 3 stuff here:

window.mainloop()