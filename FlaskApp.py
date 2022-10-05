#!/usr/bin/env python
import os
import db_helper
import random
import string
import re
import uuid

from datetime import datetime
from flask import Flask, render_template, flash, request, url_for, redirect, json, jsonify
from itsdangerous import URLSafeSerializer
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')
jwt = JWTManager(app)

s = URLSafeSerializer('IntegrateRiskCalculator')


#
# def randomString(stringLength):
#     letters = string.ascii_lowercase
#     return ''.join(random.choice(letters) for i in range(stringLength))

def randomString():
    """ Generate a unique 32 characters random_code
    """
    return uuid.uuid4().hex


def goBack(req):
    return redirect(req.headers.get("Referer"))


def read_json(fname):
    return json.load(open(fname, encoding="utf-8"))


RC_lex = {}
questions_lex = {}
options_lex = {}
answers_lex = {}
links_lex = {}
survey_list = {}
survey_questions = {}
survey_options = {}
survey_answers = {}
survey_completed = {}

answers_RC = db_helper.rc_answers.find_one({"Answer": 1})

answers_RC_lex = {}

for i in range(1, 9):
    answers_RC_lex[i] = db_helper.rc_answers.find_one({"Answer": i})


def get_RC_answers(language, index):
    answerLan = db_helper.rc_answers.find_one({language: {"$exists": True}})
    # print("in getRCanswers function, language is: ", language)
    answerLanguage = answerLan.get(language)
    answerNumber = answerLanguage.get("Answer {}".format(index)) if answerLanguage else ""
    return answerNumber



tags_update = db_helper.tokens_tags
survey_tags_update = db_helper.tokens_survey
query = {}

available_languages = ["en", "it", "lt", "hr"]

for lan in available_languages:
    RC_lex[lan] = read_json("RiskCalculatorText_{}.json".format(lan))
    survey_list[lan] = read_json("Questionnaire_{}.json".format(lan))
    survey_completed[lan] = read_json("Questionnaire_completed_{}.json".format(lan))
    questions_lex[lan] = RC_lex[lan]["questions"]
    options_lex[lan] = RC_lex[lan]["options"]
    answers_lex[lan] = RC_lex[lan]["answers"]
    links_lex[lan] = RC_lex[lan]["links"]


@app.route('/create_token', methods=['GET'])
def create_token():
    virtual_id = randomString()
    ret = {
        'access_token': create_access_token(identity=virtual_id),
        'refresh_token': create_refresh_token(identity=virtual_id)
    }
    # print("token created:", ret)
    return jsonify(ret), 200


@app.route('/refresh_token', methods=['GET'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    # print("in refresh_token, current user is: ", current_user)
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    username = get_jwt_identity()
    return jsonify(logged_in_as=username), 200


def get_tags(query, tag):
    tag_value = db_helper.tokens_tags.find_one(query, {tag: 1, "_id": 0})
    if not tag_value:
        tag_value = {tag: False}
    return tag_value


def get_language(request, query):
    data = request.get_json()
    language = data.get("language") or db_helper.tokens_tags.find_one(query, {"LANGUAGE": 1, "_id": 0})["LANGUAGE"]
    # print("in get language function, language is: ", language)
    return language


def get_all_tags(query, excludeHIV):
    findMultipleTags = db_helper.tokens_tags.find_one(query, {"HIV+": 1, "PARTNER_HIV+": 1,
                                                              "PWID_SHARE": 1,
                                                              "PWID_NO_SHARE": 1,
                                                              "MSM": 1, "NO_VACCINE_B": 1, "MIGRANT": 1,
                                                              "NO_TB_SCREENING": 1,
                                                              "_id": 0
                                                              })
    # print("from db returned as: " + str(findMultipleTags))
    filterTrueTags = list(dict(filter(lambda el: el[1] is True, findMultipleTags.items())).keys())

    print("Within get all tags function, filtered tags are returned as: ", str(filterTrueTags))

    if excludeHIV is True:
        labelsToRemove = ['HIV+', 'PARTNER_HIV+']
        label = list(set(filterTrueTags) - set(labelsToRemove))
        print ("after HIV tag removal: " + str(label))
    else:
        label = list(set(filterTrueTags))
        print ("without HIV tag removal: " + str(label))
    # PWID_NO_SHARE_tag = False
    # PWID_SHARE_tag = db_helper.tokens_tags.find_one(query, {"PWID_SHARE": 1, "_id": 0})
    # print("PWID_SHARE_tag is:", PWID_SHARE_tag, 'and PWID_NO_SHARE_tag is: ', PWID_NO_SHARE_tag)
    # if not PWID_SHARE_tag:
    #     PWID_NO_SHARE_tag = True
    # db_helper.tokens_tags.update(query, {"$set": {"PWID_NO_SHARE": PWID_NO_SHARE_tag}})


    keyorder = ['HIV+', 'PARTNER_HIV+', 'MIGRANT', 'MSM', 'NO_TB_SCREENING', 'NO_VACCINE_B', 'PWID_NO_SHARE',
                'PWID_SHARE']
    label.sort(key=keyorder.index)

    print("Within get all tags function, filtered and sorted tags are returned as: ", label)
    return label


def insertIconClass(answerText):
    tagClassSub = re.sub('<p class = "answerRC pwidShare">', '<p class = "answerRC pwidShare"><img class="svg-icon" '
                                                             'src="/riskradar/static/images/risk_kit/pwidShare.svg" '
                                                             'alt="pwidShare icon">', answerText)

    tagClassSub = re.sub('<p class = "answerRC pwidNoShare">',
                         '<p class = "answerRC pwidNoShare"><img class="svg-icon" '
                         'src="/riskradar/static/images/risk_kit/pwidNoShare.svg" '
                         'alt="pwidNoShare icon">', tagClassSub)

    tagClassSub = re.sub('<p class = "answerRC msm">', '<p class = "answerRC msm"><img class="svg-icon" '
                                                       'src="/riskradar/static/images/risk_kit/msm.svg" '
                                                       'alt="msm icon">', tagClassSub)

    tagClassSub = re.sub('<p class = "answerRC tb">', '<p class = "answerRC tb"><img class="svg-icon" '
                                                      'src="/riskradar/static/images/risk_kit/tb.svg" '
                                                      'alt="tb icon">', tagClassSub)

    tagClassSub = re.sub('<p class = "answerRC migrant">', '<p class = "answerRC migrant"><img class="svg-icon" '
                                                           'src="/riskradar/static/images/risk_kit/migrant.svg" '
                                                           'alt="migrant icon">', tagClassSub)
    return tagClassSub


def get_condom_tags(query):
    findCondomTags = db_helper.tokens_tags.find_one(query, {"ALLERGY": 1, "FEELING": 1, "LOOSE": 1, "RIGHT": 1,
                                                            "TIGHT": 1, "SHORT": 1, "_id": 0})
    # print("from db condom tags returned as: " + str(findCondomTags))
    filterTrueCondomTags = list(dict(filter(lambda el: el[1] is True, findCondomTags.items())).keys())

    # print("Within get all tags function, filtered tags are returned as: ", str(filterTrueCondomTags))
    label = list(set(filterTrueCondomTags))
    # print ("True condom tags: " + str(label))

    condomKeyOrder = ['ALLERGY', 'FEELING', 'LOOSE', 'RIGHT', 'TIGHT', 'SHORT']
    label.sort(key=condomKeyOrder.index)

    # print("Within get all tags function, filtered and sorted tags are returned as: ", label)
    return label


def get_condom_answers(language):
    condomAnswerLan = db_helper.condom_answers.find_one({language: {"$exists": True}})
    condomAnswer = condomAnswerLan.get(language)
    return condomAnswer


@app.route('/q1', methods=['GET', 'POST'])
@jwt_required
def q1():
    data = request.get_json()
    language = data["language"]
    # print(data)
    # print(request.headers)

    token = get_jwt_identity()

    db_helper.tokens_tags.delete_many({"TOKEN": token})

    userInfo = {"TOKEN": token,
                "LANGUAGE": language,
                "TIMESTAMP": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                "MSM": False,
                "HIV+": False,
                "PARTNER_HIV+": False,
                "BOTH_HIV+": False,
                "UNPROTECTED": False,
                "PWID": False,
                "PWID_SHARE": False,
                "PWID_NO_SHARE": False,
                "NO_VACCINE_B": False,
                "MIGRANT": False,
                "NO_TB_SCREENING": False,
                "FEELING": False,
                "TIGHT": False,
                "LOOSE": False,
                "SHORT": False,
                "RIGHT": False,
                "ALLERGY": False
                }
    db_helper.tokens_tags.insert_one(userInfo)

    options = options_lex[language]
    questions = questions_lex[language]
    data = {
        "question": questions["q1"],
        "options": [
            {
                "option_man": options["option_man"]
            },
            {
                "option_woman": options["option_woman"]
            },
            {
                "option_transwoman": options["option_transwoman"]
            },
            {
                "option_transman": options["option_transman"]
            }
        ],
        "answer": "",
        "links": []
    }
    send_dict = {"path": "ans_q1", "data": data}
    return jsonify(send_dict)


def q2(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)
    # print ("q2 language is: ", language)

    options = options_lex[language]
    questions = questions_lex[language]
    # print("Q2 question is: ", questions["q2"])

    data = {
        "question": questions["q2"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"],
            },
        ],
        "answer": "",
        "links": []

    }
    return data


def q3(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q3"],
        "options": [
            {
                "option_HIV": options["option_HIV"]
            },
            {
                "option_partnerHIV": options["option_partnerHIV"]
            },
            {
                "option_bothHIV": options["option_bothHIV"]
            },
            {
                "option_unprotected": options["option_unprotected"]
            },
            {
                "option_drugs": options["option_drugs"],
            },
            {
                "option_curious": options["option_curious"],
            }
        ],
        "answer": "",
        "links": []
    }
    return data


def q4(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q4"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            }
        ],
        "answer": "",
        "links": []
    }
    return data


def q5(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q5"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            }
        ],
        "answer": "",
        "links": []
    }
    return data


def q6(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q6"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            },
            {
                "option_dontknow": options["option_dontknow"]
            }

        ],
        "answer": "",
        "links": []
    }
    return data


def q7(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q7"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            }
        ],
        "answer": "",
        "links": []
    }
    return data


def q8(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q8"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            }
        ],
        "answer": "",
        "links": []
    }
    return data


def q9(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q9"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            },
            {
                "option_dontknow": options["option_dontknow"]
            }

        ],
        "answer": "",
        "links": []
    }
    return data


def q10(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q10"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            },
            {
                "option_dontknow": options["option_dontknow"]
            }

        ],
        "answer": "",
        "links": []
    }
    return data


def q11(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q11"] if get_tags(query, "MSM")["MSM"] is False else questions["q11"].replace("or "
                                                                                                             "vaginal ",
                                                                                                             "").replace(
            " o vaginale", "").replace("arba vaginalinių", "").replace("ili vaginalni", ""),
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            }

        ],
        "answer": "",
        "links": []
    }
    return data


def q12(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q12"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            }

        ],
        "answer": "",
        "links": []
    }
    return data


def q13(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)
    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q13"],
        "options": [
            {
                "option_bothHIV": options["option_bothHIV"]
            },
            {
                "option_HIV": options["option_HIV"]
            },
            {
                "option_partnerHIV": options["option_partnerHIV"]
            },
            {
                "option_no": options["option_no"]
            },
            {
                "option_dontknow": options["option_dontknow"]
            },

        ],
        "answer": "",
        "links": []
    }
    return data


def q14(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q14"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            },
            {
                "option_dontknow": options["option_dontknow"]
            }

        ],
        "answer": "",
        "links": []
    }
    return data


def q15(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    questions["q11"] if get_tags(query, "MSM")["MSM"] is False else questions["q11"].replace

    data = {
        "question": questions["q15"].replace("Hai[Il/la tuo/a partner ha[Tu e il/la tuo/a partner", "Hai") if get_tags(
            query, "HIV+")["HIV+"] is True else questions["q15"].replace("Hai[Il/la tuo/a partner ha[Tu e il/la tuo/a partner avete", "Il/la tuo/a partner ha").replace("Do you", "Does your partner") if get_tags(query, "PARTNER_HIV+")["PARTNER_HIV+"] is True else questions["q15"].replace("Hai[Il/la tuo/a partner ha[Tu e il/la tuo/a partner avete", "Tu e il/la tuo/a partner avete") if get_tags(query, "BOTH_HIV+")["BOTH_HIV+"] else questions["q15"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            },
            {
                "option_dontknow": options["option_dontknow"]
            }

        ],
        "answer": "",
        "links": []
    }
    return data


def q16(request, token):
    query = {"TOKEN": token}

    language = get_language(request,query)
    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["q16"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"]
            },
            {
                "option_dontknow": options["option_dontknow"]
            }

        ],
        "answer": "",
        "links": []
    }
    return data


def ans1(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)
    links = links_lex[language]
    excludeHIV = True
    label = get_all_tags(query, excludeHIV)
    print("Tags are: ", label)
    # print("label retrieved in ans1:" + str(label))

    stringLabel = ' '.join(label)
    # print(stringLabel)

    data = {
        "question": "",
        "options": [],
        "answer": insertIconClass(get_RC_answers(language, 1).get(stringLabel)) if stringLabel in get_RC_answers(
            language, 1).keys() else
        insertIconClass(get_RC_answers(language, 1)[
                            'DEFAULT']),
        "links": [links["link_got_it"], links["link_retake"]]
    }
    # print(stringLabel)
    # print (data)
    return data


def ans2(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)
    answers = answers_lex[language]
    links = links_lex[language]

    excludeHIV = True
    label = get_all_tags(query, excludeHIV)
    print("Tags are: ", label)

    stringLabel = ' '.join(label)

    data = {
        "question": "",
        "options": [],
        "answer": insertIconClass(get_RC_answers(language, 2).get(stringLabel)) if stringLabel in get_RC_answers(
            language, 2).keys() else
        insertIconClass(get_RC_answers(language, 2)[
                            'DEFAULT']),
        "links": [links["link_got_it"], links["link_retake"], links["link_condom"]]
    }
    return data


def ans3(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)
    answers = answers_lex[language]
    links = links_lex[language]

    excludeHIV = True
    label = get_all_tags(query, excludeHIV)
    print("Tags are: ", label)

    stringLabel = ' '.join(label)

    data = {
        "question": "",
        "options": [],
        "answer": insertIconClass(get_RC_answers(language, 3).get(stringLabel)) if stringLabel in get_RC_answers(
            language, 3).keys() else
        insertIconClass(get_RC_answers(language, 3)[
                            'DEFAULT']),
        "links": [links["link_got_it"], links["link_retake"]]
    }
    return data


def ans4(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)
    answers = answers_lex[language]
    links = links_lex[language]

    excludeHIV = True
    label = get_all_tags(query, excludeHIV)
    print("Tags are: ", label)

    stringLabel = ' '.join(label)

    data = {
        "question": "",
        "options": [],
        "answer": insertIconClass(get_RC_answers(language, 4).get(stringLabel)) if stringLabel in get_RC_answers(
            language, 4).keys() else
        insertIconClass(get_RC_answers(language, 4)[
                            'DEFAULT']),
        "links": [links["link_got_it"], links["link_retake"]]
    }
    return data


def ans5(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)
    answers = answers_lex[language]
    links = links_lex[language]

    excludeHIV = True
    label = get_all_tags(query, excludeHIV)
    print("Tags are: ", label)

    stringLabel = ' '.join(label)

    data = {
        "question": "",
        "options": [],
        "answer": insertIconClass(get_RC_answers(language, 5).get(stringLabel)) if stringLabel in get_RC_answers(
            language, 5).keys() else
        insertIconClass(get_RC_answers(language, 5)[
                            'DEFAULT']),
        "links": [links["link_got_it"], links["link_retake"]]
    }
    return data


def ans6(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)
    answers = answers_lex[language]
    links = links_lex[language]

    excludeHIV = False
    label = get_all_tags(query, excludeHIV)
    print("Tags are: ", label)

    stringLabel = ' '.join(label)
    whichIsHIV = "HIV+" if "HIV+" in label else "PARTNER_HIV+"

    data = {
        "question": "",
        "options": [],
        "answer": insertIconClass(get_RC_answers(language, 6).get(stringLabel)) if stringLabel in get_RC_answers(
            language, 6).keys() else
        insertIconClass(get_RC_answers(language, 6).get('DEFAULT ' + whichIsHIV)),
        "links": [links["link_got_it"], links["link_retake"]]
    }
    return data


def ans7(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)
    answers = answers_lex[language]
    links = links_lex[language]

    excludeHIV = False
    label = get_all_tags(query, excludeHIV)
    print("Tags are: ", label)

    stringLabel = ' '.join(label)
    whichIsHIV = "HIV+" if "HIV+" in label else "PARTNER_HIV+"

    data = {
        "question": "",
        "options": [],
        "answer": insertIconClass(get_RC_answers(language, 7).get(stringLabel)) if stringLabel in get_RC_answers(
            language, 7).keys() else
        insertIconClass(get_RC_answers(language, 7).get('DEFAULT ' + whichIsHIV)),
        "links": [links["link_got_it"], links["link_retake"]]
    }
    return data


def ans8(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)
    answers = answers_lex[language]
    links = links_lex[language]

    excludeHIV = True
    label = get_all_tags(query, excludeHIV)
    print("Tags are: ", label)

    stringLabel = ' '.join(label)
    # print("Language in answer8 is: ", language)
    # print(get_RC_answers(language, 8))
    data = {
        "question": "",
        "options": [],
        # "answer": insertIconClass(answers_RC_lex[8][stringLabel]) if stringLabel in answers_RC_lex[8].keys() else
        # insertIconClass(answers_RC_lex[8][
        #                     'DEFAULT']),
        "answer": insertIconClass(get_RC_answers(language, 8).get(stringLabel)) if stringLabel in get_RC_answers(language, 8).keys(

        ) else
        insertIconClass(get_RC_answers(language, 8)[
                            'DEFAULT']),
        "links": [links["link_got_it"], links["link_retake"]]
    }
    # print("in answer8, tags are:", stringLabel)
    return data


@app.route('/cq1', methods=['POST'])
@jwt_required
def cq1():
    data = request.get_json()
    token = get_jwt_identity()

    query = {"TOKEN": token}

    db_helper.tokens_tags.update({"TOKEN": token}, {"$set": {"ALLERGY": False, "FEELING": False, "RIGHT": False,
                                                                 "TIGHT": False, "SHORT": False, "LOOSE": False}})

    if "language" in data:
        language = data["language"]
        language_tag = {"$set": {"LANGUAGE": language}}
        tags_update.update_one(query, language_tag)
    else:
        language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    # print("jusqu'ici tout va bien...")
    data = {
        "question": questions["condom_q1"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"],
            },
        ],
        "answer": "",
        "links": []
    }
    send_dict = {"path": "ans_cq1", "data": data, "token": token}
    return jsonify(send_dict)


def cq2(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["condom_q2"],
        "options": [
            {
                "option_tight": options["option_tight"]
            },
            {
                "option_short": options["option_short"],
            },
            {
                "option_loose": options["option_loose"]
            },
            {
                "option_right": options["option_right"],
            }
        ],
        "answer": "",
        "links": []

    }
    return data


def cq3(request, token):
    query = {"TOKEN": token}
    language = get_language(request,query)

    options = options_lex[language]
    questions = questions_lex[language]

    data = {
        "question": questions["condom_q3"],
        "options": [
            {
                "option_yes": options["option_yes"]
            },
            {
                "option_no": options["option_no"],
            },
        ],
        "answer": "",
        "links": []
    }
    return data


# + (answers["condom_ans_noproblem"]

def anscondom(request, token):
    # "answer": insertIconClass(get_RC_answers(language, 8).get(stringLabel)) if stringLabel in get_RC_answers(language,
    #                                                                                                          8).keys(
    #
    # )
    query = {"TOKEN": token}
    language = get_language(request,query)
    condomAnswer = get_condom_answers(language)
    condomLabel = get_condom_tags(query)
    links = links_lex[language]

    stringCondomLabel = ' '.join(condomLabel)
    #
    # data = {
    #     "question": "",
    #     "options": [],
    #     "answer": answers["condom_ans_intro"] + (answers["condom_ans_feeling"] if get_tags(query, "FEELING")["FEELING"] is True else answers["condom_ans_nofeeling"])
    #               + (answers["condom_ans_allergy"] if get_tags(query, "ALLERGY")["ALLERGY"] is True else answers["condom_ans_noallergy"])
    #               + (answers["condom_ans_advice"]) + (answers["condom_ans_allergic"] if get_tags(query, "ALLERGY")["ALLERGY"] is True else "")
    #               + (answers["condom_ans_bigger"] if (get_tags(query, "TIGHT")["TIGHT"]) is True or (get_tags(query, "SHORT")["SHORT"]) is True else "")
    #               + (answers["condom_ans_allergic_bigger"] if ((get_tags(query, "ALLERGY")["ALLERGY"]) and (get_tags(query, "TIGHT")["TIGHT"])) is True else "")
    #               + (answers["condom_ans_allergic_loose"] if (get_tags(query, "ALLERGY")["ALLERGY"]) and (get_tags(query, "LOOSE")["LOOSE"]) is True else "")
    #               + (answers["condom_ans_thinner"] if get_tags(query, "FEELING")["FEELING"] is False else "")
    #               + (answers["condom_ans_allergic_thinner"] if ((get_tags(query, "ALLERGY")["ALLERGY"]) is True and (get_tags(query, "FEELING")["FEELING"]) is False) else ""),
    #     "links": [links["link_got_it"], links["link_retake"], links["link_retake_condom"]]
    # }

    data = {
        "question": "",
        "options": [],
        "answer": condomAnswer[stringCondomLabel],
        "links": [links["link_got_it"], links["link_retake"]]
    }

    return data


@app.route('/ans_q1', methods=['POST'])
@jwt_required
def ans_q1():
    data = request.get_json()
    # print(data)
    # print(request.headers)

    token = get_jwt_identity()
    # print(token)

    # token = data["token"]
    # print("data received is:", data)
    path, data = ("ans_q2", q2(request, token)) if (data["answer"] == "option_man" or data["answer"] ==
                                               "option_transwoman") \
        else ("ans_q3", q3(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q2', methods=['POST'])
@jwt_required
def ans_q2():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    new_tag = {"$set": {"MSM": True}}
    tags_update.update_one(query, new_tag) if data["answer"] == "option_yes" else ""
    path, data = ("ans_q3", q3(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q3', methods=['POST'])
@jwt_required
def ans_q3():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    tag = "HIV+" if data["answer"] == "option_HIV" else "PARTNER_HIV+" if data["answer"] == "option_partnerHIV" \
        else "BOTH_HIV+" if data["answer"] == "option_bothHIV" else "UNPROTECTED" \
        if data["answer"] == "option_unprotected" else "PWID" if data["answer"] == "option_drugs" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    tag = "HIV+" if data["answer"] == "option_bothHIV" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    path, data = ("ans_q5", q5(request, token)) if data["answer"] == "option_drugs" else ("ans_q4", q4(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q4', methods=['POST'])
@jwt_required
def ans_q4():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    tag = "PWID" if data["answer"] == "option_yes" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    path, data = ("ans_q5", q5(request, token)) if data["answer"] == "option_yes" else ("ans_q6", q6(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q5', methods=['POST'])
@jwt_required
def ans_q5():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    tag = "PWID_SHARE" if data["answer"] == "option_yes" else "PWID_NO_SHARE"
    # print("In ans_q5, PWID tags are: ", tag)
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    path, data = ("ans_q6", q6(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q6', methods=['POST'])
@jwt_required
def ans_q6():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    tag = "" if data["answer"] == "option_yes" else "NO_VACCINE_B"
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    path, data = ("ans_q7", q7(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


# @app.route('/ans_q7', methods=['POST'])
# @jwt_required
# def ans_q7():
#     data = request.get_json()
#
#     token = get_jwt_identity()
#     query = {"TOKEN": token}
#     tag = "MIGRANT" if data["answer"] == "option_yes" else ""
#     if tag != "":
#         new_tag = {"$set": {tag: True}}
#         tags_update.update_one(query, new_tag)
#     path, data = ("ans_q8", q8(request, token)) if get_tags(query, "MIGRANT")["MIGRANT"] is True else ("ans_q10", q10(request, token)) if \
#     get_tags(query, "UNPROTECTED")["UNPROTECTED"] is False \
#         else ("ans_q14", q14(request, token)) if get_tags(query, "HIV+")["HIV+"] is True else ("ans_q15", q15(request, token)) if \
#     get_tags(query, "PARTNER_HIV+")["PARTNER_HIV+"] is True else ("ans3", ans3(request, token)) \
#         if get_tags(query, "BOTH_HIV+")["BOTH_HIV+"] is True else ("ans_q13", q13(request, token))
#     send_dict = {"path": path, "data": data, "links": "", "token": token}
#
#     return jsonify(send_dict)

@app.route('/ans_q7', methods=['POST'])
@jwt_required
def ans_q7():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    tag = "MIGRANT" if data["answer"] == "option_yes" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    path, data = ("ans_q8", q8(request, token)) if get_tags(query, "MIGRANT")["MIGRANT"] is True else ("ans_q10", q10(request, token)) if \
    get_tags(query, "UNPROTECTED")["UNPROTECTED"] is False \
        else ("ans_q14", q14(request, token)) if get_tags(query, "HIV+")["HIV+"] is True else ("ans_q15", q15(request, token)) if \
    get_tags(query, "PARTNER_HIV+")["PARTNER_HIV+"] is True else ("ans3", ans3(request, token)) \
        if get_tags(query, "BOTH_HIV+")["BOTH_HIV+"] is True else ("ans_q13", q13(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)

# @app.route('/ans_q8', methods=['POST'])
# @jwt_required
# def ans_q8():
#     data = request.get_json()
#
#     token = get_jwt_identity()
#     path, data = ("ans_q9", q9(request, token)) if data["answer"] == "option_yes" else ("ans_q10", q10(request, token)) if \
#     get_tags(query, "UNPROTECTED")["UNPROTECTED"] is False \
#         else ("ans_q14", q14(request, token)) if get_tags(query, "HIV+")["HIV+"] is False else ("ans_q15", q15(request, token)) if \
#     get_tags(query, "PARTNER_HIV+")["PARTNER_HIV+"] is False else ("ans3", ans3(request, token)) \
#         if get_tags(query, "BOTH_HIV+")["BOTH_HIV+"] is False else ("ans_q13", q13(request, token))
#     send_dict = {"path": path, "data": data, "links": "", "token": token}
#
#     return jsonify(send_dict)

@app.route('/ans_q8', methods=['POST'])
@jwt_required
def ans_q8():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("ans_q9", q9(request, token)) if data["answer"] == "option_yes" else ("ans_q10", q10(request, token)) if \
    get_tags(query, "UNPROTECTED")["UNPROTECTED"] is False \
        else ("ans_q14", q14(request, token)) if get_tags(query, "HIV+")["HIV+"] is False else ("ans_q15", q15(request, token)) if \
    get_tags(query, "PARTNER_HIV+")["PARTNER_HIV+"] is False else ("ans3", ans3(request, token)) \
        if get_tags(query, "BOTH_HIV+")["BOTH_HIV+"] is False else ("ans_q13", q13(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)

@app.route('/ans_q9', methods=['POST'])
@jwt_required
def ans_q9():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    tag = "" if data["answer"] == "option_yes" else "NO_TB_SCREENING"
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    path, data = ("ans_q10", q10(request, token)) if get_tags(query, "UNPROTECTED")["UNPROTECTED"] is False else (
    "ans_q14", q14(request, token)) if get_tags(query, "HIV+")["HIV+"] is True else \
        ("ans_q15", q15(request, token)) if get_tags(query, "PARTNER_HIV+")["PARTNER_HIV+"] is True else ("ans3", ans3(request, token)) \
            if get_tags(query, "BOTH_HIV+")["BOTH_HIV+"] is True else ("ans_q13", q13(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q10', methods=['POST'])
@jwt_required
def ans_q10():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("ans_q11", q11(request, token)) if data["answer"] == "option_yes" else ("ans8", ans8(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q11', methods=['POST'])
@jwt_required
def ans_q11():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    path, data = ("ans_q12", q12(request, token)) if data["answer"] == "option_yes" else ("ans1", ans1(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q12', methods=['POST'])
@jwt_required
def ans_q12():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    path, data = ("ans_q13", q13(request, token)) if data["answer"] == "option_no" else ("ans2", ans2(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q13', methods=['POST'])
@jwt_required
def ans_q13():
    data = request.get_json()

    token = get_jwt_identity()
    query = {"TOKEN": token}
    tag = "HIV+" if data["answer"] == "option_HIV" else "PARTNER_HIV+" if data["answer"] == "option_partnerHIV" else \
        "BOTH_HIV+" if data["answer"] == "option_bothHIV" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    path, data = ("ans3", ans3(request, token)) if data["answer"] == "option_bothHIV" else ("ans_q14", q14(request, token)) \
        if data["answer"] == "option_HIV" else ("ans_q15", q15(request, token)) if data["answer"] == "option_partnerHIV" \
        else ("ans_q16", q16(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q14', methods=['POST'])
@jwt_required
def ans_q14():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("ans_q15", q15(request, token)) if data["answer"] == "option_yes" else ("ans_q16", q16(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q15', methods=['POST'])
@jwt_required
def ans_q15():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("ans4", ans4(request, token)) if data["answer"] == "option_yes" else ("ans_q16", q16(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans_q16', methods=['POST'])
@jwt_required
def ans_q16():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("ans6", ans6(request, token)) if data["answer"] == "option_yes" else ("ans7", ans7(request, token))
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/ans1', methods=['POST'])
@jwt_required
def ans_1():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("", ans1(request, token))
    links = [{"Retake Quiz": "/q1"}]
    send_dict = {"path": path, "data": data, "links": links, "token": token}

    return jsonify(send_dict)


@app.route('/ans2', methods=['POST'])
@jwt_required
def ans_2():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("", ans2(request, token))
    links = [{"Retake Quiz": "/q1"}, {"Condom Test": "/cq1"}]
    send_dict = {"path": path, "data": data, "links": links, "token": token}

    return jsonify(send_dict)


@app.route('/ans3', methods=['POST'])
@jwt_required
def ans_3():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("", ans3(request, token))
    links = [{"Retake Quiz": "/q1"}]
    send_dict = {"path": path, "data": data, "links": links, "token": token}

    return jsonify(send_dict)


@app.route('/ans4', methods=['POST'])
@jwt_required
def ans_4():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("", ans4(request, token))
    links = [{"Retake Quiz": "/q1"}]
    send_dict = {"path": path, "data": data, "links": links, "token": token}

    return jsonify(send_dict)


@app.route('/ans5', methods=['POST'])
@jwt_required
def ans_5():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("", ans5(request, token))
    links = [{"Retake Quiz": "/q1"}]
    send_dict = {"path": path, "data": data, "links": links, "token": token}

    return jsonify(send_dict)


@app.route('/ans6', methods=['POST'])
@jwt_required
def ans_6():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("", ans6(request, token))
    links = [{"Retake Quiz": "/q1"}]
    send_dict = {"path": path, "data": data, "links": links, "token": token}

    return jsonify(send_dict)


@app.route('/ans7', methods=['POST'])
@jwt_required
def ans_7():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("", ans7(request, token))
    links = [{"Retake Quiz": "/q1"}]
    send_dict = {"path": path, "data": data, "links": links, "token": token}

    return jsonify(send_dict)


@app.route('/ans8', methods=['POST'])
@jwt_required
def ans_8():
    data = request.get_json()

    token = get_jwt_identity()
    path, data = ("", ans8(request, token))
    links = [{"Retake Quiz": "/q1"}]
    send_dict = {"path": path, "data": data, "links": links, "token": token}

    return jsonify(send_dict)


@app.route('/ans_cq1', methods=['POST'])
@jwt_required
def ans_cq1():
    data = request.get_json()

    token = get_jwt_identity()

    path = "ans_cq2"

    query = {"TOKEN": token}
    tag = "FEELING" if data["answer"] == "option_yes" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)

    data = cq2(request, token)
    send_dict = {"path": path, "data": data, "links": "", "token": token}
    return jsonify(send_dict)


@app.route('/ans_cq2', methods=['POST'])
@jwt_required
def ans_cq2():
    data = request.get_json()

    token = get_jwt_identity()

    query = {"TOKEN": token}
    tag = "TIGHT" if data["answer"] == "option_tight" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    tag = "LOOSE" if data["answer"] == "option_loose" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    tag = "SHORT" if data["answer"] == "option_short" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)
    tag = "RIGHT" if data["answer"] == "option_right" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)

    data = cq3(request, token)

    path = "anscondom"
    send_dict = {"path": path, "data": data, "links": "", "token": token}

    return jsonify(send_dict)


@app.route('/anscondom', methods=['POST'])
@jwt_required
def ans_condom():
    data = request.get_json()

    token = get_jwt_identity()

    query = {"TOKEN": token}
    tag = "ALLERGY" if data["answer"] == "option_yes" else ""
    if tag != "":
        new_tag = {"$set": {tag: True}}
        tags_update.update_one(query, new_tag)

    path, data = ("", anscondom(request, token))

    send_dict = {"path": path, "data": data, "token": token}

    return jsonify(send_dict)


@app.route('/survey/<language>', methods=['GET'])
def survey(language):
    data = survey_list[language]

    return jsonify(data)


@app.route('/survey_answers', methods=['POST'])
@jwt_required
def survey_answers():
    data = request.get_json()
    submitted_survey_answers = data["answers"]
    language = data["language"]
    token = get_jwt_identity()

    userAnswer = {"TOKEN": token,
                "LANGUAGE": language,
                "TIMESTAMP": datetime.now(),
                "SURVEY_Q1": 0,
                "SURVEY_Q2": 0,
                "SURVEY_Q3": 0,
                "SURVEY_Q4": 0,
                "SURVEY_Q5": 0,
                "SURVEY_Q6": 0,
                "SURVEY_Q7": 0,
                "SURVEY_Q8_SUPPORTIVE": 0,
                "SURVEY_Q8_EASY": 0,
                "SURVEY_Q8_EFFICIENT": 0,
                "SURVEY_Q8_CLEAR": 0,
                "SURVEY_Q8_EXCITING": 0,
                "SURVEY_Q8_INTERESTING": 0,
                "SURVEY_Q8_INVENTIVE": 0,
                "SURVEY_Q8_LEADINGEDGE": 0,
                "SURVEY_Q9": 0
                }
    # print("userInfo to insert:", userInfo)
    db_helper.tokens_survey.insert_one(userAnswer)


    query = {"TOKEN": token}
    submitted_survey = {"$set": {"SURVEY_Q1": submitted_survey_answers[0][0], "SURVEY_Q2":
        submitted_survey_answers[1],
                                 "SURVEY_Q3": submitted_survey_answers[2][0], "SURVEY_Q4": submitted_survey_answers[3],
                                 "SURVEY_Q5": submitted_survey_answers[4][0], "SURVEY_Q6": submitted_survey_answers[5][0],
                                 "SURVEY_Q7": submitted_survey_answers[6][0],
                                 "SURVEY_Q8_SUPPORTIVE": submitted_survey_answers[7][
                                     0],
                                 "SURVEY_Q8_EASY": submitted_survey_answers[7][1], "SURVEY_Q8_EFFICIENT":
                                     submitted_survey_answers[7][
                                         2],
                                 "SURVEY_Q8_CLEAR": submitted_survey_answers[7][3], "SURVEY_Q8_EXCITING":
                                     submitted_survey_answers[
                                         7][4], "SURVEY_Q8_INTERESTING": submitted_survey_answers[7][5],
                                 "SURVEY_Q8_INVENTIVE":
                                     submitted_survey_answers[7][6],
                                 "SURVEY_Q8_LEADINGEDGE": submitted_survey_answers[7][7],
                                 "SURVEY_Q9": submitted_survey_answers[8][0]}
                        }
    # print("Submitted answers: ", submitted_survey_answers)
    survey_tags_update.update_one(query, submitted_survey)

    survey_completed_text = survey_completed[language]["completed_message"]["text"]

    ret_data = {"token": token, "text": survey_completed_text}

    return jsonify(ret_data)

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
