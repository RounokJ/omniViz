#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 23:15:11 2020

MIT License
Copyright (c) 2020 Rounok Joardar
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@author: Rounok Joardar
"""

#imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.font_manager as font_manager
matplotlib.use("TkAgg")
import tkinter as tk
import pandas as pd
from scipy import stats
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

#modules
import support_functions as supp
import globalvars as globy

#omniViz plot functions

def plot_handler(plot_frame):
    print(globy.plot_type)
    if globy.plot_type == "linear regression":
        stockPlot_linreg(plot_frame)
    elif globy.plot_type == "time series":
        stockPlot_timeseries(plot_frame)


def stockPlot_linreg(plot_frame):
    fig, ax = plt.subplots(ncols=1, figsize=(8.25,4.0), dpi=100)
    axLblFont = font_manager.FontProperties(family='Calibri', weight='bold', style='normal', size=10)
    #actual plot code
    #x-axis is always going to be time.
    x_axes = 'Date'
    #mask dataframe by the dates in the date range
    date_range = (supp.read_listbox(globy.listchain[0].lbox))
    mask = globy.stock_data[x_axes].isin(date_range)
    masked_data = globy.stock_data[mask]
    
    #get list of unique stocks
    list_of_stocks = supp.get_unique('Ticker', globy.stock_data)
    #get the closing prices of all datasets 
    close_prices = pd.DataFrame(supp.get_unique('Date', masked_data))
    close_prices.columns = ['Date']
    for stock in list_of_stocks:
        temp = masked_data.loc[masked_data['Ticker'] == stock, 'Adj Close']
        close_prices = close_prices.join(temp.to_frame(name=stock))
    # calculate gross returns
    close_prices.drop('Date', axis=1, inplace=True)
    returns = close_prices.pct_change(1)
    temp = pd.DataFrame(supp.get_unique('Date', masked_data))
    temp.columns = ['Date']
    gross_returns = returns.join(temp)
    gross_returns = gross_returns.dropna(axis=0)  # drop first missing row
    #print(gross_returns.head())
    #calculate log returns
    returns = np.log(close_prices) - np.log(close_prices.shift(1))
    log_returns = returns.join(temp)
    log_returns = log_returns.dropna(axis=0)  # drop first missing row
    print(log_returns.head())
    
    x = log_returns[list_of_stocks[0]].tolist()
    y = log_returns[list_of_stocks[1]].tolist()
    slope, intercept, r, p, std_err = stats.linregress(x, y)
    
    def capm(x):
        return slope * x + intercept
        
    mymodel = list(map(capm, x))
    log_returns['linreg'] = mymodel
        
    #plot
    lgnd = list_of_stocks[0:2]
    #check if log scale is desired for either axis
#    if y_log.get():
#        plt.yscale('log')
#    if x_log.get():
#        plt.xscale('log')
    log_returns.plot.scatter(x=list_of_stocks[0], y=list_of_stocks[1], c='none', edgecolors='b', fig=fig, ax=ax, label=lgnd)
    log_returns.plot(x=list_of_stocks[0], y='linreg', fig=fig, ax=ax, color='r')
    
    #plot design code
    ax.grid(linestyle='--', color='lightgray')
    ax.set_xlabel(list_of_stocks[0], fontproperties=axLblFont, color='k')
    ax.set_ylabel(list_of_stocks[1], fontproperties=axLblFont, color='k')
    #frame 3 contains the graph    
    graph_frame = tk.Frame(plot_frame)
    graph_frame.grid(row=0, column=0)
    
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill="none", expand=1)

    toolbar = NavigationToolbar2Tk(canvas, graph_frame)
    toolbar.update()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
    

def stockPlot_timeseries(plot_frame):
    fig, ax = plt.subplots(ncols=1, figsize=(8.25,4.0), dpi=100)
    lgndFont = font_manager.FontProperties(family='Calibri', weight='normal', style='normal', size=8)
    axLblFont = font_manager.FontProperties(family='Calibri', weight='bold', style='normal', size=10)
    axFont = font_manager.FontProperties(family='Calibri', weight='normal', style='normal', size=8)
    #actual plot code
    #x-axis is always going to be time.
    x_axes = 'Date'
    #mask dataframe by the dates in the date range
    date_range = (supp.read_listbox(globy.listchain[0].lbox))
    mask = globy.stock_data[x_axes].isin(date_range)
    masked_data = globy.stock_data[mask]
    
    #y-axis has to plot each user selection for each stock individually
    list_of_stocks = supp.get_unique('Ticker', globy.stock_data)
    chainlink = 1
    for stock in list_of_stocks:
        y_axes = supp.read_listbox(globy.listchain[chainlink].lbox)
        dfilt = masked_data.loc[masked_data['Ticker'] == stock]
        chainlink = chainlink + 1
        for elem in y_axes:
            lgnd = stock + ' : ' + elem
            #check if log scale is desired for either axis
            #if y_log.get():
                #plt.yscale('log')
            #if x_log.get():
                #plt.xscale('log')
            dfilt.plot(x=x_axes, y=elem, x_compat=True, fig=fig, ax=ax, rot=90, label=lgnd)
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontproperties(axFont)
        ax.legend()
        handles, labels = ax.get_legend_handles_labels()
        lgd = dict(zip(labels, handles))
        ax.legend(lgd.values(), lgd.keys(), bbox_to_anchor=(1.04,1), loc="upper left", prop=lgndFont)
        fig.subplots_adjust(left=0.25, right=0.75, bottom=0.225)

    #plot design code
    ax.grid(linestyle='--', color='lightgray')
    ax.set_xlabel(x_axes, fontproperties=axLblFont, color='b')
    ax.set_ylabel(y_axes[0], fontproperties=axLblFont, color='b')
    
    #frame 3 contains the graph    
    graph_frame = tk.Frame(plot_frame)
    graph_frame.grid(row=0, column=0)
    
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill="none", expand=1)

    toolbar = NavigationToolbar2Tk(canvas, graph_frame)
    toolbar.update()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)