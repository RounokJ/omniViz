#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 17:01:14 2020

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
import pandas as pd
import yfinance as yf 
#modules
import support_functions as supp
import searchlist as sly
import globalvars as globy

# this function takes ticker name(s) as input
# pulls data from yahoo, start/end date from config file
# and returns it as a pandas dataframe
# then creates a listchain from that dataframe
def pull_stock_data(configpath, lcf_bundle, preset=False):
    #unpack bundle
    listchain_frame = lcf_bundle[0]
    nb = lcf_bundle[1]
    ent_browse = lcf_bundle[2]
    #reset stock_data to empty
    globy.stock_cols = []
    globy.stock_data = pd.DataFrame()
    #setup local variables
    startdate = supp.get_from_config(configpath, "start_date")
    enddate = supp.get_from_config(configpath, "end_date")
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
        globy.stock_data = globy.stock_data.append(temp)
        globy.stock_cols = list(data.columns)
    #once dataframe is made, create and populate the listchain
    #push dataframe metadata to log window
    print(globy.stock_data.info())
    create_listchain(globy.stock_data, listchain_frame, nb, preset)
    
def create_listchain(df, listchain_frame, nb, preset=False):
    #clear pre-existing listchain if any
    supp.clear_listchain(listchain_frame, nb)
    listchain_names = ['Date Range']
    list_of_stocks = supp.get_unique('Ticker', df)
    for stock in list_of_stocks:
        listchain_names.append(stock)
    first = True #this lets us handle the Date SearchList independent of the others
    chainlength = len(listchain_names)
    chainlink = 0
    globy.listchain = []
    current_tab = listchain_frame[nb.index("current")]
    for link in range(chainlength):
        if first:
            link = sly.Searchlist(listchain_names[chainlink], current_tab, 'extended', immortal=True)
            globy.listchain.append(link)
            link.populate_listbox(list(df['Date']))
            first = False
        else:
            link = sly.Searchlist(listchain_names[chainlink], current_tab, 'multiple')
            globy.listchain.append(link)
            link.populate_listbox(globy.stock_cols)
        chainlink = chainlink + 1
    #load preset values if call is made to config
    if preset:
        supp.load_preset_vals()
