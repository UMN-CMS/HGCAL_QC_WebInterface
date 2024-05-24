# HGCAL-WagonDB
CGI scripts for HGCAL wagon testing information

There are three different websites contained within cgi-bin: WagonDB, EngineDB, and LabelDB.
These website are used to visualize the data from the Databases in meanful ways
Some scripts or functions within scripts are also used by the Testing GUI

The Wagon and Engine pages share much of the same code, with the exception of the Database they query and the testing data displayed.
A base script (base.py) creates the Webpage, loads Bootstrap, Bokeh, and d3, and creates the header and footer seen on all webpages.
base.header(title) and base.top() are called at the start of the webpage code and base.bottom() is called at the end.
All HTML written in between is then placed in between in the main body of the webpage.
The HTML is written in print() statements as comments.

connect.py provides the connection to the Database using mysql.connector. 
connect.connect(0) reads from the Database and connect.connect(1) writes to it.
This is implemented in pages that interact with the Database in the following way:
from connect import connect
db = connect(0 or 1)
cur = db.cursor()

db is the connection to the database and db.cursor allows you to send commands to the database with cur.execute()
Items are retrieved from the database with cur.fetchall() or cur.fetchone()

All data except for the test results is pulled directly from the database using cur.execute().
This data is then formatted properly before being implemented onto the website using HTML.

The test results data is plotted using a package called Bokeh. 
Bokeh creates the proper HTML and Javascript to create plots, widgets, tables, etc that are written in python.
Since these are all objects created in HTML and Javascript, they can update dynamically without refreshing the webpage.
This allows for lots of filtering and customization within these plots but requires a bit of extra work.
First, it's a lot easier to create .csv files containing all of the testing data and import these files than it is to
query the database every time. These .csv files are used to make pandas dataframes, which can easily be merged
before using them to create a ColumnDataSource. A ColumnDataSource is a Bokeh object that acts like a data table. 
It can be created from a python dictionary or pandas dataframe easily and is compatible with both Python and Javascript,
so it acts as a go-between when transferring data back and forth.

The majority of plotting documentation is found in WagonDB/bit_error_ratePlots.py. 
Here is where general Bokeh syntax, widgets, plots, filters, and creating Bokeh visual objects are explained.
Any duplicate code in later files isn't explained. Each script is a bit different, anything new is always explained.

Many scripts are in both WagonDB and EngineDB and have nearly identical code. In these cases, only the WagonDB file is documented.
If there are differences in the EngineDB scripts, these variations are documented.
