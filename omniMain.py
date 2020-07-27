#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 15:09:48 2020

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
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
#modules
import intake_functions as intake
import searchlist as sly
import omniPlot as omplot
import support_functions as supp
import globalvars as globy

ver = '2.0.0'

#omniViz main class
class MainGUI:
    #three frame structure
    def __init__(self, master):
        self.master = master   
        master.title('stockViz ver ' + ver)
    #menu toolbar contains some selectable user options
        menubar = tk.Menu(master)
        file = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=file)
        file.add_command(label='Load', command= lambda: intake.pull_stock_data())
        file.add_separator()
        file.add_command(label='Save State', command= lambda: supp.prompt_user_to_name_state())
        file.add_command(label='Load State', command= lambda: supp.load_from_config(globy.configpath, self.lcf_bundle))
        file.add_command(label='Config', command= lambda: supp.modify_config())
        file.add_separator()
        file.add_command(label='Exit', command= lambda: supp.callback(master))
    
        prefs = tk.Menu(menubar, tearoff = 0) 
        menubar.add_cascade(label ='Preferences', menu=prefs) 
        prefs.add_command(label ='View Settings', command=None) 
    
        help_ = tk.Menu(menubar, tearoff = 0) 
        menubar.add_cascade(label ='Help', menu=help_) 
        help_.add_command(label ='User Guide', command=None) 
        help_.add_separator() 
        help_.add_command(label ='About omniViz', command=supp.about)

        master.config(menu=menubar)
    #top level contains all the common selectable user options 
        self.user_select_frame = tk.Frame(master)
        self.user_select_frame.pack(side='top')
        #frame 1, column order
        ent_browse_col = 0
        #column 1 is skipped because ent_browse has columnspan = 2
        load_button_col = 2
        load_from_config_button_col = 3
        reset_button_col = 4
        frame_log_options_col = 5
        plot_button_col = 6

        # entry box for ticker names
        self.ent_browse=tk.Entry(self.user_select_frame, font=myFont)
        self.ent_browse.grid(row=0, column=ent_browse_col, columnspan=2, sticky='EW',
                             padx=(listBoxPadx,listBoxPadx))
        self.ent_browse.bind("<Return>", 
                             lambda keypress: intake.pull_stock_data(globy.configpath, self.lcf_bundle))

        # load button to pull stock data from yahoo
        self.load_button=tk.Button(self.user_select_frame, text="Load", font=myFont, 
                                   command= lambda: intake.pull_stock_data(globy.configpath, self.lcf_bundle))
        self.load_button.grid(row=0, column=load_button_col, padx=(2,2))


        ## this function can now be found in the file menu under "Load State"
        # load button to pull stock data from stocks that are listed 
        # in the the config file, instead of by user input
        load_from_config_button=tk.Button(self.user_select_frame, text="Load Config", font=myFont,
                                          command= lambda: supp.load_from_config(globy.configpath, self.lcf_bundle))
        load_from_config_button.grid(row=0, column=load_from_config_button_col, padx=(2,2))

        # plot button
        plot_button=tk.Button(self.user_select_frame, text="Plot", font=myFont,
                              command= lambda: omplot.plot_handler(self.plot_frame))
        plot_button.grid(row=0, column=plot_button_col, padx=(2,2))
        
        # reset button
        reset_button=tk.Button(self.user_select_frame, text="Reset", font=myFont,
                               command= lambda: supp.clear_listchain(self.listchain_frame, self.nb))
        reset_button.grid(row=0, column=reset_button_col, padx=(2,2))

        #frame_log_options contains the log scale options
        self.frame_log_options = tk.Frame(self.user_select_frame)
        self.frame_log_options.grid(row=0, column=frame_log_options_col)
        #label for log scale checkboxes
        self.loglabel = tk.Label(self.frame_log_options, text="Use log scale:", font=myFont)
        self.loglabel.pack(side='top')
        #checkbox to change y-axis to log scale
        self.y_log = tk.IntVar()
        self.cb1 = tk.Checkbutton(self.frame_log_options, text="y-axis", font=myFont, variable=self.y_log)
        self.cb1.pack(side='top')
        #checkbox to change x-axis to log scale
        self.x_log = tk.IntVar()
        self.cb2 = tk.Checkbutton(self.frame_log_options, text="x-axis", font=myFont, variable=self.x_log)
        self.cb2.pack(side='top')
    #middle layer contains listchain
        #and is located inside a notebook widget to allow for tabs
        self.nb = ttk.Notebook(master)
        self.page1 = ttk.Frame(self.nb)
        self.page2 = ttk.Frame(self.nb)
        self.listchain_frame = [self.page1, self.page2]

        self.nb.add(self.page1, text='One')
        self.nb.add(self.page2, text='Two')

        self.nb.pack(expand=1, fill="both")
    #bottom layer contains the plot
        self.plot_frame = tk.Frame(master)
        self.plot_frame.pack(side='top')
    #variable bundle to make shorter function calls
        #listchain_frame, nb, and ent_browse bundlded together as a list
        self.lcf_bundle = [self.listchain_frame, self.nb, self.ent_browse]
        
        
#main
root = tk.Tk()
#general style
myFont = tkfont.Font(family="Calibri", size=8, weight="normal")
z_len = myFont.measure("0")
scrnWid = root.winfo_screenwidth()
scrnFrac = 0.6
numListBoxes = 10
listBoxWid = int(scrnWid * scrnFrac / numListBoxes / z_len)
listBoxHt = 5
listBoxPadx = int(listBoxWid/5)
listBoxPady = int(listBoxWid/5)
#tab style
s = ttk.Style()
s.configure('TNotebook.Tab', font=myFont)
#setup modules
sly.setup(root)
supp.setup(root)
globy.init()
#call main clss
app = MainGUI(root)
root.mainloop()