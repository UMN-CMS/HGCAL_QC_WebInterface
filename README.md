# HGCAL Web API
CGI scripts for HGCAL QC testing information

There are three different websites contained within cgi-bin: WagonDB, EngineDB, and LabelDB.
The Wagon and Engine webpages are used to visualize the data from the databases in meanful ways
The Label webpages are used to provide some back end functions related to labeling.
Some scripts or functions within scripts are also used by the Testing GUI

The Wagon and Engine pages share much of the same code, with the exception of the Database they query and the testing data displayed.
A base script (base.py) creates the Webpage, loads Bootstrap, Bokeh, and d3, and creates the header and footer seen on all webpages.
base.header(title) and base.top() are called at the start of the webpage code and base.bottom() is called at the end.
All HTML written in between is then placed in between in the main body of the webpage.
The HTML is written in print() statements.
This is how cgi works, thus each script must print a cgi header, something like `Content-type: text/html`

connect.py provides the connection to the Database using mysql.connector. 
connect.connect(0) reads from the Database and connect.connect(1) writes to it.
This is implemented in pages that interact with the Database in the following way:
from connect import connect
db = connect(0 or 1)
cur = db.cursor()

db is the connection to the database and db.cursor allows you to send commands to the database with cur.execute()
Items are retrieved from the database with cur.fetchall() or cur.fetchone()

Test results plots and some tables are created using a package called Bokeh. 
Bokeh creates the proper HTML and Javascript to create plots, widgets, tables, etc that are written in python.
Since these are all objects created in HTML and Javascript, they can update dynamically without refreshing the webpage.
This allows for lots of filtering and customization within these plots but requires a bit of extra work.
