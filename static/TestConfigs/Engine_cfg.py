masterCfg = {
    # Order of tests matters here
    # This should be the same order that you want the tests to be run in
    # Number of test will also be decide by this list so don't miss any
    "Test": [
        # First Look
        {
            "name": "Visual Inspection",
            "required": 1,
            "desc_short": "Purely Visual Inspection",
            "desc_long": "Inspect for obvious visual damage or other anomalies.",
        },
        # Pre-power up
        {
            "name": "LDO Resistance",
            "required": 1,
            "desc_short": "Measure resistance of LDO resistors.",
            "desc_long": "LDO output resistors: R912 and R907: should be 500kOhm",
        },
        {
            "name": "Short Check",
            "required": 1,
            "desc_short": "Check for obvious shorts",
            "desc_long": "Check that there is resistance between power and ground.",
        },
        # Power Up Sequence
        {
            "name": "Voltage/Current Check",
            "required": 1,
            "desc_short": "Check the voltage and current",
            "desc_long": "Check that the voltage and current on the power supply are at correct values.",
        },
        # Component Checks
        {
            "name": "R911",
            "required": 1,
            "desc_short": "Check component R911 or TP901",
            "desc_long": "R911 or TP901: output voltage of the LDO: should be close to 1.20V",
        },
        {
            "name": "C906/C908",
            "required": 1,
            "desc_short": "Check component C906 and C908",
            "desc_long": "C906/908: should be equal to the input voltage of the LDO: O(1.3–1.8V), depending on how the power supply was configured",
        },
        {
            "name": "C909/C907/C901",
            "required": 1,
            "desc_short": "Check component C909, C907, and C901",
            "desc_long": "C909/907/901: should be equal to the input voltage for the linPOL: O(10V)",
        },
        {
            "name": "R905/R903/C902/C903",
            "required": 1,
            "desc_short": "Check components R905/R903/C902/C903",
            "desc_long": "R905/906 and C902/903: outputs of the linPOL, should both be at 2.5V",
        },
        {
            "name": "TP902",
            "required": 1,
            "desc_short": "Probe TP902",
            "desc_long": "TP902: test point for linpol output power (TX channel)",
        },
        {
            "name": "R916",
            "required": 1,
            "desc_short": "Check component R916",
            "desc_long": "R916: between the TX and RX outputs of the linPOL. Should be 0V",
        },
        {
            "name": "C807/C808/C809/C801",
            "required": 1,
            "desc_short": "Check components C807/C808/C809/C801",
            "desc_long": "C807/808/809/801: Should be 1.2V (goes to VTRX+)",
        },
        # Operations Tests
        {
            "name": "Fast Command",
            "required": 1,
            "desc_short": "Check fast command functionality",
            "desc_long": "Verify fast command operability by manipulating counters on encoder and decoder.",
        },
        {
            "name": "lpGBT ",
            "required": 1,
            "desc_short": "Check components C807/C808/C809/C801",
            "desc_long": "C807/808/809/801: Should be 1.2V (goes to VTRX+)",
        },
        {
            "name": "lpGBT IC/EC communication",
            "required": 1,
            "desc_short": "Check operability of lpGBT IC/EC communication",
            "desc_long": "Read and write to lpBGT registers via ICEC. Check DAQ lpGBT read of registers via IC. Check Trigger lpGBTs: successful read registers via EC. Ensure write and readback to user ID registers (0x004 - 0x007)",
        },
        {
            "name": "lpGBT setup",
            "required": 1,
            "desc_short": "Ensure setup can be performed",
            "desc_long": "Perform nominal setup from BE. Do setup, link trick, setup. Check PUSMStatus (0x1d9) reports READY (0x13) for all 3 lpGBTs. Check lpGBTs locked to BE All 3 RX equal within 200 Hz. Check All 3 RX-DV equal within 200 Hz",
        },
        {
            "name": "GPIO functionality",
            "required": 1,
            "desc_short": "Check the quality of the GPIOs",
            "desc_long": "Read and write to all GPIO channels and verify levels. Write nominal configuration and then toggle each line one-by-one and verify change in both lpGBT status and voltage level",
        },
        {
            "name": "ADC functionality",
            "required": 1,
            "desc_short": "Check quality of the ADCs",
            "desc_long": "Measure known voltages/resistances. Check measured values for all 4 gains within tolerances",
        },
        {
            "name": "Uplink quality",
            "required": 1,
            "desc_short": "Check the quality of the uplinks",
            "desc_long": "PRBS validation from lpGBTs. Check bit error rate below threshold.",
        },
        {
            "name": "Downlink quality",
            "required": 1,
            "desc_short": "Check the quality of the downlinks",
            "desc_long": "Eye opening test. Check eye opening width and height below threshold.",
        },
        {
            "name": "Elink quality",
            "required": 1,
            "desc_short": "Check the quality of the elinks",
            "desc_long": "PRBS validation from and back to ZCU. Check bit error rate below threshold.",
        },
    ],
    # Example of information needed for tests (from Wagon config)
    # Use template dictionary above
    # FOLLOW THE FORMAT EXPICITLY PLEASE :)
    # "Test": [
    #    {"name": "Resistance Measurement", "required": 1, "desc_short": "Measure resistance of analog lines", "desc_long": "Test must be completed before attempting to measure ID resistor"},
    #    {"name": "ID Resistor Measurement", "required": 1, "desc_short": "Measure resistance of ID resistor", "desc_long": "Must be completed after the general resistance measurement"},
    #    {"name": "I2C Read/Write", "required": 1, "desc_short": "Check I2C read/write along wagon", "desc_long": "Test must be completed before BERT for wagon wheel configuration"},
    #    {"name": "Bit Error Rate Test", "required": 1, "desc_short": "Determine quality of data transmission", "desc_long": "Needs to be completed after I2C check in order to set up wagon wheel"},
    # ],
    # List of board types (e.g. major/minor type serial number differences)
    # Mostly important for wagons but allows for support of different engine
    # production versions if necessary
    # requiredTests field should match the indices of the list above
    # (e.g. if Test2 is required for Engine V3 Right, this list should include 1
    "Board_type": [
        {
            "name": "Engine V3 Right",
            "type_sn": "100300",
            "requiredTests": [0, 1, 2, 3, 4],
        },
        {
            "name": "Engine V3 Left",
            "type_sn": "100310",
            "requiredTests": [0, 1, 2, 3, 4],
        },
    ],
    # People who you would like to add as testers by default
    # HGCAL_dev can be used for debug testing in the beginning
    # The GUI will require everyone to have their own "account"
    "People": [
        "Nadja",
        "Charlie",
        "Bryan",
        "Devin",
        "HGCAL_dev",
    ],
    # Information for sending and receiving data to/from the database
    # Needs to be different based on board type
    "DBInfo": {
        "name": "EngineDB",
        "reader": "EngineDBReadUser",
        "inserter": "EngineDBInserter",
        "admin": "EngineDBInserter",
        "baseURL": "http://cmslab3.spa.umn.edu/~cros0400/cgi-bin/EngineDB/",
    },
}
