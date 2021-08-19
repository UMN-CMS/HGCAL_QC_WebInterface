import json

f = open('example.json')

data = json.loads(f.read())

f.close()
