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
                'ADC_functionality.py',
                'EClockData.py',
                'ELinkQualityData.py',
                'ELinkQualityData1.py',
                'ELinkQualityData2.py',
                'ELinkQualityData3.py',
                'ELinkQualityData4.py',
                'ELinkQualityData5.py',
                'ELinkQualityData6.py',
                'ELinkQualityData7.py',
                'ELinkQualityData8.py',
                'ELinkQualityData9.py',
                'ELinkQualityData10.py',
                'ELinkQualityData11.py',
                'ELinkQualityData12.py',
                'ELinkQualityData13.py',
                'ELinkQualityData14.py',
                'ELinkQualityData15.py',
                'ELinkQualityData16.py',
                'ELinkQualityData17.py',
                'ELinkQualityData18.py',
                'ELinkQualityData19.py',
                'ELinkQualityData20.py',
                'FastCommandQualityData.py',
                'X_PWRData.py',
                'UplinkQuality.py',
                'I2CData.py',
                'search.py',
             ]
    return scripts

def looped_pages():
    scripts = {'Serial Numbers': ['module.py'],
                'Subtypes': ['summary_board.py'],
                'People': ['tester_summary2.py'],
             }
    return scripts

def get_db_name():
    return 'EngineDB'

def get_paths():
    paths = ['../../static_html',
            '../../static_html/EngineDB/',
            '../../static_html/files/',
            '../../static_html/files/enginedb',
            ]
    return paths