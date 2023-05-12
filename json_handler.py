import json


with open('files/pharmit.json', 'r') as file:
    session = json.load(file)

farm = session["points"]
print(farm[1]["name"])
