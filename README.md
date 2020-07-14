# omniViz
general purpose data visualizer 

July 14th Update

 New functionality and features

-reset button added, clears entire listchain
-close, aka 'x' buttons to remove links from listchain
-config json file added, contains start and end dates and save states
-can now load data from preset save states
-basic fix of searchlist class, make_searchlist() function should have always been run at instantiation, now it actually is doing that
-added ability to make either axis a log scale. which is not helpful for stockdata, and should not be confused for log returns, but you can do that now if you want
-date range searchlist is actually online now, so you can use subsets of the pulled data without having to reset config file and re-pull each time