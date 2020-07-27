#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 17:11:22 2020

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

#support functions

#imports
import json
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
#modules
import intake_functions as intake
import searchlist as sly
import globalvars as globy

#settings
def setup(root):
    global myFont
    global listBoxHt
    global listBoxWid
    myFont = tkfont.Font(root=root, family="Calibri", size=8, weight="normal")
    z_len = myFont.measure("0")
    scrnWid = root.winfo_screenwidth()
    scrnFrac = 0.6
    numListBoxes = 10
    listBoxWid = int(scrnWid * scrnFrac / numListBoxes / z_len)
    listBoxHt = 5

####################################
#functions to interact with configs#
####################################
#read from config
def read_config(path):
    try:
        with open(path) as jsonfile:
            data = json.load(jsonfile)
    except:
        print("ERROR: file not found")
    return data

#get toplevel data from config
def get_from_config(path, key):
    data = read_config(path)
    return data.get(key,"ERROR: Value not found")

def load_from_config(configpath, lcf_bundle):
    #unpack bundle
    listchain_frame = lcf_bundle[0]
    nb = lcf_bundle[1]
    #clear pre-existing listchain if any
    clear_listchain(listchain_frame, nb)
    #when load from config button is pressed, start from here
    data = read_config(configpath)
    statelist_key = "states" #all the states are listed under this key
    statenames = sorted(data[statelist_key].keys())
    #make a searchlist, with statebox specific code, to contain all the states
    current_tab = listchain_frame[nb.index("current")]
    state_select = sly.Searchlist("Select State", current_tab, 'browse', statebox=True, lcf_bundle=lcf_bundle)
    state_select.populate_listbox(statenames)
    
def modify_config():
    new_window = tk.Tk()
    #labels
    startdate_label = tk.Label(new_window, text="start date", font=myFont)
    startdate_label.grid(row=0, column=0)
    enddate_label = tk.Label(new_window, text="end date", font=myFont)
    enddate_label.grid(row=1, column=0)
    plot_type_label = tk.Label(new_window, text="plot type", font=myFont)
    plot_type_label.grid(row=2, column=0)
    #values/user options
    #start/end date
    startdate_entbox = tk.Entry(new_window, width=20, font=myFont)
    startdate_entbox.grid(row=0, column=1)
    enddate_entbox = tk.Entry(new_window, width=20, font=myFont)
    enddate_entbox.grid(row=1, column=1)
    startdate = get_from_config(globy.configpath, "start_date")
    enddate = get_from_config(globy.configpath, "end_date")
    startdate_entbox.insert(0, startdate)
    enddate_entbox.insert(0, enddate)
    #plot type
    plot_type_var = tk.StringVar(new_window)
    plot_type_var.set(globy.plot_types_list[0]) # default value
    plot_type_dropdown = tk.OptionMenu(new_window, plot_type_var, *globy.plot_types_list)
    plot_type_dropdown.grid(row=2, column=1)
    #apply button
    apply_button=tk.Button(new_window, text="Apply", font=myFont, 
                           command= lambda: edit_config(startdate_entbox, enddate_entbox, plot_type_var, new_window))
    apply_button.grid(row=3, column=1)
    new_window.mainloop()
    
def edit_config(startdate_entbox, enddate_entbox, plot_type_var, new_window):
    #read from entboxes
    new_startdate = {"start_date": startdate_entbox.get()}
    new_enddate = {"end_date": enddate_entbox.get()}
    #open config
    config = read_config(globy.configpath)
    #update dates
    config.update(new_startdate)
    config.update(new_enddate)
    #save config
    save_config(config)
    #update plot type
    globy.plot_type = plot_type_var.get()
    new_window.destroy()
    
#save the config file itself
def save_config(new_config):
    try:
        with open(globy.configpath, 'w') as config_file:
            json.dump(new_config, config_file, indent=4)
    except:
        print("ERROR: could not save to config file")

#save a state to the config file     
def save_to_config(statename, configfilepath, new_window):  
    config = read_config(configfilepath)
    stockticks = []
    presetvals = []
    stockticks_string = ""
    for link in globy.listchain:
        stockticks.append(link.name)
        presetvals.append(link.sbox.get())
    for ticker in stockticks[1:]:
        stockticks_string += ticker
        stockticks_string += ","
    stockticks_string = stockticks_string.rstrip(',')
    state = {
    statename: {
  		"stock_tickers": stockticks_string,
  		"preset_vals": {
  			"Date Range": presetvals[0]
  		}
  	}}
    config["states"].update(state)
    for ticker, vals in zip(stockticks[1:], presetvals[1:]):
        new_preset = {ticker:vals}
        config["states"][statename]["preset_vals"].update(new_preset)
    save_config(config)
    new_window.destroy()

###############################
#functions to save/load states#
###############################
#once a state is selected, get the tickerlist stored in that state
#and create a listchain using that list
def select_state(configpath, statebox, lcf_bundle):
    global preset_vals
    #unpack bundle
    ent_browse = lcf_bundle[2]
    data = read_config(configpath)
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
    intake.pull_stock_data(configpath, lcf_bundle, preset=True)
    
def remove_state(statebox):
    data = read_config()
    #all states are listed under this key
    statelist_key = "states"
    #get the specifc state the user selected as a list
    state = read_listbox(statebox)
    del data[statelist_key][state[0]]
    save_config(data)
    load_from_config()

def prompt_user_to_name_state():
    #Save ____ to <configfilepath> [SAVE]
    new_window = tk.Tk()
    #Label
    thewordSave = tk.Label(new_window, text="Save", font=myFont)
    thewordSave.pack(side='left')
    #Entrybox
    enterStatename = tk.Entry(new_window, width=5, font=myFont)
    enterStatename.pack(side='left')
    enterStatename.bind("<Return>", lambda keypress: save_to_config(enterStatename.get(),
                                                         configfilepath_entbox.get(), 
                                                         new_window))
    #Label
    thewordTo = tk.Label(new_window, text="to", font=myFont)
    thewordTo.pack(side='left')
    #Entrybox
    configfilepath_entbox = tk.Entry(new_window, width=20, font=myFont)
    configfilepath_entbox.pack(side='left')
    configfilepath_entbox.insert(0, globy.configfilepath)
    #Button
    savebutton=tk.Button(new_window, text="Save", font=myFont, 
                         command= lambda: save_to_config(enterStatename.get(),
                                                         configfilepath_entbox.get(), 
                                                         new_window))
    savebutton.pack(side='left')
    new_window.mainloop()

def load_preset_vals():
    #given preset values, put them into their corresponding listchainlinks
    #with the double for loop strategy you dont even need to have your 
    #config json in the same order as your tickerlist
    for key in preset_vals:
        temp = preset_vals.get(key)
        for link in globy.listchain:
            if str(link.name) == str(key):
                link.sbox.insert(0, temp)
                link.run_searchbox()
                break


#################
#other functions#
#################
def clear_listchain(listchain_frame, nb):
    current_tab = listchain_frame[nb.index("current")]
    # destroy all widgets from frame
    for widget in current_tab.winfo_children():
       widget.destroy()
       
def get_unique(column, data):
     return data[column].unique().tolist()

def read_listbox(lbox):
    sel = []
    for index in lbox.curselection():
        sel.append(lbox.get(index))
    return sel

#creates popup when closing out of the interface
def callback(window):
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            window.quit()

def about():
    messagebox.showinfo("omniViz", 
                        "omniViz is a general purpose data intake and visualization GUI")
    
