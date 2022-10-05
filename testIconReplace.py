import db_helper
import re

answers_RC_lex = {}
for i in range(1, 9):
    answers_RC_lex[i] = db_helper.rc_answers.find_one({"Answer": i})
    #print (answers_RC_lex[i])

answerText = answers_RC_lex[1]["PWID_SHARE MSM MIGRANT"]
print ("Testing LEX: " + answerText)

tagClassSub = re.sub('<p class = "answerRC pwidShare">', '<p class = "answerRC pwidShare"><img class="svg-icon" '
                                                       'src="http://83.212.115.126/images/risk/pwidShare.svg" '
                                                       'alt="pwidShare icon">', answerText)

tagClassSub = re.sub('<p class = "answerRC pwidNoShare">', '<p class = "answerRC pwidNoShare"><img class="svg-icon" '
                                                       'src="http://83.212.115.126/images/risk/pwidNoShare.svg" '
                                                       'alt="pwidNoShare icon">', tagClassSub)

tagClassSub = re.sub('<p class = "answerRC msm">', '<p class = "answerRC msm"><img class="svg-icon" '
                                                       'src="http://83.212.115.126/images/risk/msm.svg" '
                                                       'alt="msm icon">', tagClassSub)

tagClassSub = re.sub('<p class = "answerRC tb">', '<p class = "answerRC tb"><img class="svg-icon" '
                                                       'src="http://83.212.115.126/images/risk/tb.svg" '
                                                       'alt="tb icon">', tagClassSub)

tagClassSub = re.sub('<p class = "answerRC migrant">', '<p class = "answerRC migrant"><img class="svg-icon" '
                                                       'src="http://83.212.115.126/images/risk/migrant.svg" '
                                                       'alt="migrant icon">', tagClassSub)


print("After sub", tagClassSub)
