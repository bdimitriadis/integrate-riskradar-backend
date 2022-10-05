import db_helper

answers_RC = db_helper.condom_answers_db.find_one({"Condom Answers": 1})
print(answers_RC)