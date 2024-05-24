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

def looped_pages():
    scripts = {'Serial Numbers': ['module.py'],
                'Subtypes': ['summary_board.py'],
                'People': ['tester_summary2.py'],
                'Attachments': ['get_attach.py'],
             }
    return scripts

def get_db_name():
    return 'WagonDB'

def get_paths():
    paths = ['../../static_html',
            '../../static_html/WagonDB/',
            '../../static_html/files/',
            '../../static_html/files/wagondb',
            ]
    return paths
