#!./cgi_runner.sh

import argparse
import add_test_functions_engine
import connect
import getpass
import importlib.util
import json

def load_config(path):

    base = path.split("/")[-1][:-3]

    spec = importlib.util.spec_from_file_location(base, path)
    cfg = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(cfg)
    
    config = cfg.masterCfg
    return config

def add_tests(test_list, passwd):

    order = 1
    for test in test_list:
        print("Adding new test type: {}".format(test["name"]))
        try:
            add_test_functions_engine.add_new_test(test["name"], test["required"], test["desc_short"], test["desc_long"], order, passwd)
            order += 1
        except Exception as e:
            print("Test malformated or already in DB: {}. Check config file before proceeding.".format(test["name"]))
            quit()

def add_people(people_list, passwd):

    for person in people_list:
        print("Adding new tester: {}".format(person))
        try:
            add_test_functions_engine.add_tester(person, passwd)
        except Exception as e:
            print("Tester could not be added to the database: {}. Check config file before proceeding.".format(person))
            quit()

def add_boards(board_type_list, passwd):
    
    for board in board_type_list:
        print("Adding new board type: {}".format(board["name"]))
        try:
            add_test_functions_engine.add_board_type(board["name"], board["type_sn"], board["requiredTests"], passwd)
        except Exception as e:
            print(e)
            print("Board type could not be added: {}. Check config file before proceeding".format(board["name"]))
            quit()

    
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--config", action="store", type=str, help="Input path for config (should be a static directory)")

    args = parser.parse_args()

    # Get configuration file with test types, people, board types, and DB info
    try:

        config = load_config(args.config)

    except Exception as e:

        print("No file found")
        quit()

    passwd = getpass.getpass(prompt="{} Admin Password: ".format(config["DBInfo"]["name"]))

    # Password verification
    try:

        conn = connect.connect_admin(passwd)

    except Exception as e:

        print("Invalid Password. Try Again.")
        quit()

    print("\n-----------------------------")
    print("  DB Connection Established  ")
    print("-----------------------------\n")

    add_tests(config["Test"], passwd)
    add_boards(config["Board_type"], passwd)
    add_people(config["People"], passwd)

    print("Database updated with information from {}!".format(args.config))

if __name__ == "__main__":
    main()
