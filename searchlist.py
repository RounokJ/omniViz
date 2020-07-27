#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 23:30:08 2020

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

#searchlist class

#imports
import tkinter as tk
import tkinter.font as tkfont

#modules
import support_functions as supp
import globalvars as globy

#settings
def setup(root):
    global myFont
    global listBoxHt
    global listBoxWid
    myFont = tkfont.Font(family="Calibri", size=8, weight="normal")
    z_len = myFont.measure("0")
    scrnWid = root.winfo_screenwidth()
    scrnFrac = 0.6
    numListBoxes = 10
    listBoxWid = int(scrnWid * scrnFrac / numListBoxes / z_len)
    listBoxHt = 5

# Searchlist class
# bundle the listbox and searchbox together
class Searchlist:
        
    def __init__(self, name, parent_frame, selectmode, immortal=False, statebox=False, lcf_bundle=[None,None,None]):
         #        ent_browse=None, listchain_frame=None, nb=None):
        self.name = name
        #make frame
        self.frame = tk.Frame(parent_frame)
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
                                    command= lambda: supp.select_state(globy.configpath, self.lbox, lcf_bundle))
            select_button.pack(side='top')   
            delete_button=tk.Button(self.searchframe, text="Delete", font=myFont, 
                                    command= lambda: supp.remove_state(self.lbox))
            delete_button.pack(side='top')   
            self.lbox.bind("<Return>", lambda keypress: supp.select_state(globy.configpath, self.lbox, lcf_bundle))
            
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
        self.frame.destroy()
        #clear out rows that contain that stock from the stock_data df
        globy.stock_data = globy.stock_data[globy.stock_data.Ticker != self.name]
        #clear the removed stock from the listchain as well
        for link in globy.listchain:
            if link.name == self.name:
                globy.listchain.remove(link)
        print(globy.stock_data.info())
        
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
        lbox_selected_vals = supp.read_listbox(self.lbox)
        if len(lbox_selected_vals) == self.lbox.size():
            self.sbox.insert(0, '*')
        else:
            self.sbox.insert(0, lbox_selected_vals)
