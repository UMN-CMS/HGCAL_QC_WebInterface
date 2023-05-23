# Some CGI script for plotting test data

# Pull everything from database that we want
# Write out the correct MySQL
# Store as pandas dataframe
# Put in another python file (probably)
def get_data():
    pass

# ------------------
# Plot Brainstorming
# ------------------
# - Time series of how many boards have been tested/passed all tests
# - Boards completed / boards still to test
# - Leader board for testers
# - Resistance measurement:
#   - Distribution of resistances per board type 
# - ID Resistor:
#   - "        "
# - I2C Test
#   - Don't think there's anything specific
# - BERT
#   - Distributions of BER per link
#   - Same for board type
# 

def make_plots(testing_df):

    # Data manipulation...

    # Use mpl to make your plots


# CGI STUFF HERE
print("<h1> HI </h1>")

#....
data = get_data()
make_plots(data)
