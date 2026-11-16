def hd_wagon_map(short_code):
    mapping = {
            "WH30ATAA" : "WH-30AT-AAA",
            "WH30ATBA" : "WH-30AT-BBA",
            "WH30ATBB" : "WH-30AT-BBB",
            "WH30BDAA" : "WH-30BD-AAA",
            "WH30BDBA" : "WH-30BD-BBA",
            "WH30BDBB" : "WH-30BD-BBB",
            "WH30BTAA" : "WH-30BT-AAA",
            "WH30BTBA" : "WH-30BT-BBA",
            "WH30BTBB" : "WH-30BT-BBB",
            "WH30CTAA" : "WH-30CT-AAA",
            "WH30CTBA" : "WH-30CT-BBA",
            "WH30CTBB" : "WH-30CT-BBB",
            "WH30DTAA" : "WH-30DT-AAA",
            "WH30DTBA" : "WH-30DT-BBA",
            "WH30DTBB" : "WH-30DT-BBB",
            "WH31ATAA" : "WH-31AT-AAAA",
            "WH31ATBA" : "WH-31AT-BBAA",
            "WH31ATBB" : "WH-31AT-BBBB",
            "WH31BTAA" : "WH-31BT-AAAA",
            "WH31BTBA" : "WH-31BT-BBBA",
            "WH31BTBB" : "WH-31BT-BBBB",
            "WH20ATAA" : "WH-20AT-AA",
            "WH20ATBA" : "WH-20AT-BA",
            "WH20ATBB" : "WH-20AT-BB",
            "WH21ATAA" : "WH-21AT-AAA",
            "WH21ATBA" : "WH-21AT-BBA",
            "WH21ATBB" : "WH-21AT-BBB",
            "WH30ADAA" : "WH-30AD-AAA",
            "WH30ADBA" : "WH-30AD-BBA",
            "WH30ADBB" : "WH-30AD-BBB",
            "WH30CDAA" : "WH-30CD-AAA",
            "WH30CDBA" : "WH-30CD-BBA",
            "WH30CDBB" : "WH-30CD-BBB",
            "WH30DDAA" : "WH-30DD-AAA",
            "WH30DDBA" : "WH-30DD-BBA",
            "WH30DDBB" : "WH-30DD-BBB",
            "WH31ADAA" : "WH-31AD-AAAA",
            "WH31ADBA" : "WH-31AD-BBAA",
            "WH31ADBB" : "WH-31AD-BBBB",
            "WH31BDAA" : "WH-31BD-AAAA",
            "WH31BDBA" : "WH-31BD-BBAA",
            "WH31BDBB" : "WH-31BD-BBBB",
            "WH20ADAA" : "WH-20AD-AA",
            "WH20ADBA" : "WH-20AD-BA",
            "WH20ADBB" : "WH-20AD-BB",
            "WH21ADAA" : "WH-21AD-AAA",
            "WH21ADBA" : "WH-21AD-BBA",
            "WH21ADBB" : "WH-21AD-BBB",
            }
    
    long_code = mapping.get(short_code, "")

    if not long_code:
        raise KeyError("Board type not found in HD Wagon Mapping!")

    return long_code

