import pymongo

import config
from pymongo import MongoClient
from flask import json


def read_json(fname):
    return json.load(open(fname, encoding="utf-8"))


answersRC_en = read_json("rcAnswers_en.json")
answersRC_it = read_json("rcAnswers_it.json")
answersRC_lt = read_json("rcAnswers_lt.json")
answersRC_hr = read_json("rcAnswers_hr.json")
condomAnswers_en = read_json("condomAnswers_en.json")
condomAnswers_it = read_json("condomAnswers_it.json")
condomAnswers_lt = read_json("condomAnswers_lt.json")
condomAnswers_hr = read_json("condomAnswers_hr.json")

# print(answersRC["Answer 1"])

# answersRCjson = json.dumps(answersRC)
# print(answersRCjson)
# print(answersRCjson["Answer 1"])

# client = MongoClient()

conf = config.DevelopmentConfig

token = conf.TOKEN

client = MongoClient(conf.MONGO_SERVER,
                     conf.MONGO_PORT,
                     username=conf.MONGO_USERNAME,
                     password=conf.MONGO_PASSWORD,
                     authSource=conf.MONGO_AUTH_SOURCE,
                     authMechanism='SCRAM-SHA-1')

# client = MongoClient("localhost")

# Create db
db = client['risk_calculator']

# Create collection containing tokens and users' answers


tokens_tags = db.tokens_tags
userInfo = {"test": 0}

result = tokens_tags.insert_one(userInfo)

# Create collection containing users' survey answers

tokens_survey = db.tokens_survey
userAnswer = {"test": 0}

survey_result = tokens_survey.insert_one(userAnswer)

# Create collection containing RC answers text

rc_answers = db.rc_answers

for ans in range(1, 9):
    label = "Answer " + str(ans)
    answersRC_en[label].update({"Answer": ans})
    answersRC_it[label].update({"Answer": ans})
    answersRC_lt[label].update({"Answer": ans})
    answersRC_hr[label].update({"Answer": ans})


db.rc_answers.insert_one({'en': answersRC_en, 'it': answersRC_it, 'lt': answersRC_lt,
                          'hr': answersRC_hr})


# Create collection containing condom answers text


condom_answers = db.condom_answers


condom_answers.insert_one({'en': condomAnswers_en, 'it': condomAnswers_it, 'lt': condomAnswers_lt,
                              'hr': condomAnswers_hr})

client.close()
