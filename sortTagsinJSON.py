import json

def read_json(fname):
    return json.load(open(fname, encoding="utf-8"))

answersRC = read_json("rcAnswers_it_backup29Nov.json")

t = json.dumps(answersRC)
print(t)