# HGCAL Web API
CGI scripts for HGCAL QC testing information

This branch is built for deployment, capable of installing all dependencies, creating database, Apache web server, and cgi scripts.
This Web API was designed to be set up on AlmaLinux 9. The home page can be accessed with `http://localhost/Factory/exampleDB/home_page.py`

Assuming you have a machine with AlmaLinux 9 on it that is connected to a network and that you have sudo access to, follow these steps to install the interface.

1. If you haven't already, generate a new SSH key on your machine and add it to your GitHub account.
2. On GitHub, within this repository, open `setup_hgcal_db.sh` and copy its contents.
3. On your Alma 9 machine, paste the contents of your file into a new file called `setup_hgcal_db.sh`.
4. Using `chmod`, update the permissions for this file and execute it, then follow the guiding prompts.
5. Run `cd HGCAL_QC_WebInterface`, then `grep -rn "TODO"`. This will list all file changes needing to be made.
6. Create your users for your database with the desired permissions, and add these to `connect.py` after renaming the template file. See below for the permissions that the Reader and Inserter users need.
7. If you wish to access the web server from outside your local network, you will need to acquire an SSL Certificate, and likely a hostname. Once acquired, these should be added to `/etc/httpd/conf.d/ssl.conf`.

These webpages are used to visualize the data from the database in meanful ways, related to tracking the testing process.
Some scripts or functions within scripts are also used by the Testing GUI

File Structure:
- cgi-bin: contains all of the cgi scripts, this is where the Apache server looks.
- hgcal-label-info: submodule with all of the information pertaining to barcode information
- static: contains extraneous files

Database structure:
- Attachments: Holds JSON blobs containing the test data in the `attach` column. `test_id` matches the attachment to the corresponding item in the Test table. The `attachmime` field is usually filled with `text/plain`.
- Board: Holds all of the boards on record. `sn` is the numbers trailing the type code, `type_id` is the type code, and `location` references where the board is with respect to the HGCAL collaboration.
- Board_images: Holds the names of image files stored in the image directory. `board_id` matches the board to its corresponding images. `view` denotes the top or bottom of the board.
- Board_type: Holds all of the board types separated by type code (denoted `type_sn` in this table). `type_sn` in this table matches to `type_id` in Board, and `type_id` here matches to `type_id` in Type_test_stitch.
- Check_In: Holds information about receiving boards
- Check_Out: Holds information about shipping boards. `comment` is typically filled with where the board is being shipped to.
- Manufacturers: Holds all of the manufacturers that make boards for the HGCAL project and matches an id from Board to a name.
- People: Holds all of the tester names and lets Test, Check_In, and Check_Out match a name to `person_id`.
- Test: Holds test data, matching tests to boards by `board_id`.
- Test_Type: Holds all of the different test types. `relative_order` is the order that these tests should be performed. `test_type` here matches to `test_type_id` in other tables.
- Type_test_stitch: Matches board sub types to the tests that need to be done for them. The API will not allow tests to be uploaded for a board unless its subtype is matched to that test in this table.

cgi script information:
A base script (base.py) creates the Webpage, loads Bootstrap, Bokeh, and d3, and creates the header and footer seen on all webpages.
base.header(title) and base.top() are called at the start of the webpage code and base.bottom() is called at the end.
All HTML written in between is then placed in between in the main body of the webpage.
The HTML is written in print() statements.
This is how cgi works, thus each script must print a cgi header, something like `Content-type: text/html`

connect.py provides the connection to the Database using mariadb 
connect.connect(0) reads from the Database and connect.connect(1) writes to it.
This is implemented in pages that interact with the Database in the following way:
from connect import connect
db = connect(0 or 1)
cur = db.cursor()

db is the connection to the database and db.cursor allows you to send commands to the database with cur.execute()
Items are retrieved from the database with cur.fetchall() or cur.fetchone()

Some tables are created using a package called Bokeh. 
Bokeh creates the proper HTML and Javascript to create plots, widgets, tables, etc that are written in python.
Since these are all objects created in HTML and Javascript, they can update dynamically without refreshing the webpage.
This allows for lots of live filtering and customization within these plots but requires a bit of extra work.
