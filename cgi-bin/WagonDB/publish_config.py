import os

local_path = os.path.dirname(os.path.abspath(__file__))

# input all scripts that are to be converted to html
def get_pages():
    scripts = ['home_page.py',
                'testers.py',
                'checkin_summary.py',
                'checkout_summary.py',
                'summary.py',
                'tester_summary.py',
                'board_images.py',
                'testdata.py',
                'CompareTesters.py',
                'ResistanceMeasurementData.py',
                'IDResistorData.py',
                'I2CData.py',
                'BitErrorRateData.py',
                'search.py',
             ]
    return scripts

# key is the variable that is looped over, scripts then follow in a list
def looped_pages():
    scripts = {'Serial Numbers': ['module.py'],
                'Subtypes': ['summary_board.py'],
                'People': ['tester_summary2.py'],
                'Attachments': ['get_attach.py'],
             }
    return scripts

def get_db_name():
    return 'WagonDB'

# directories that need to be made
def get_paths():
    paths = ['{}/../../static_html'.format(local_path),
            '{}/../../static_html/WagonDB/'.format(local_path),
            '{}/../../static_html/files/'.format(local_path),
            '{}/../../static_html/files/wagondb'.format(local_path),
            ]
    return paths
