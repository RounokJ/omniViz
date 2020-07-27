# omniViz
general purpose data visualizer 

July 27th Update

modularized code

- main function now calls modules so the code isn't as messy
- plot functions now go through a plot_handler function, both time series and linear regression plots can be selected at the moment

July 22nd Update

adding license

July 18th Update

Save states implemented

- ability to save states to config added
- ttk notebook used to add tabs, such that multiple listchains can be uesd in parallel
- file menubar added to free up button real estate

July 14th Update

New functionality and features

-reset button added, clears entire listchain
-close, aka 'x' buttons to remove links from listchain
-config json file added, contains start and end dates and save states
-can now load data from preset save states
-basic fix of searchlist class, make_searchlist() function should have always been run at instantiation, now it actually is doing that
-added ability to make either axis a log scale. which is not helpful for stockdata, and should not be confused for log returns, but you can do that now if you want
-date range searchlist is actually online now, so you can use subsets of the pulled data without having to reset config file and re-pull each time