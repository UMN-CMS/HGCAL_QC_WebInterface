#!/usr/bin/python3

import json
import base64

def b64(attach):
    with open(attach, "r") as f:
        data = f.read()
    f.close()
   
    data_bytes = data.encode("ascii") 
    encoded = base64.b64encode(data_bytes)
    data = encoded.decode("ascii")
    return data

def main():
    test_dict = {
                    "tester"        :   "",
                    "test_type"     :   "",
                    "successful"    :   "",
                    "comments"      :   "",
                    "attach1"       :   "",
                    "attach1_desc"  :   "",
                    "attach1_com"   :   "",
                    "attach2"       :   "",
                    "attach2_desc"  :   "",
                    "attach2_com"   :   "",
                    "attach3"       :   "",
                    "attach3_desc"  :   "",
                    "attach3_com"   :   "",
                }

    test_dict['tester'] = input("Enter tester name: ")
    test_dict['test_type'] = input("Enter test type: ")
    test_dict['successful'] = input("Successful? (1 for yes, 0 for no): ")
    test_dict['comments'] = input("Comments (required): ")
    
    attachments = input("Do you have attachments to upload? (y/n): ")
    i = 1
    while(attachments == "y" or attachements == "yes"):
        if i == 4: break
        path = input("Path to attachment: ")
        desc = input("Description of attachment: ")
        comments = input("Attachment comments: ")
        if i == 1:
            test_dict['attach1'] = b64(path)
            test_dict['attach1_desc'] = desc
            test_dict['attach1_com'] = comments
        elif i == 2:
            test_dict['attach2'] = b64(path)
            test_dict['attach2_desc'] = desc
            test_dict['attach2_com'] = comments
        elif i == 3:
            test_dict['attach1'] = b64(path)
            test_dict['attach1_desc'] = desc
            test_dict['attach1_com'] = comments
        attachments = input("Do you have another attachment? (y/n): ")
        if attachments != "y" or attachments != "yes":
            break
        i += 1

    outpath = input("Ouput name for json file: ")

    if outpath[-5:] != ".json":
        outpath += ".json"

    with open(outpath, "w") as g:
        json.dump(test_dict, g)

    g.close()
            
    
    

if __name__ == "__main__":
    main()    
