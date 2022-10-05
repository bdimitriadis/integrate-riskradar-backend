import json

# import re
# unsortedLabel = ["PWID_NO_SHARE", "MSM", "NO_VACCINE_B", "MIGRANT", "NO_TB_SCREENING"]
#
# # words = unsortedLabel.split()
# # words.sort()
# # print(words)
#
# keyorder = ['HIV+', 'PARTNER_HIV+', 'PWID_SHARE', 'PWID_NO_SHARE', 'MSM', 'NO_VACCINE_B', 'MIGRANT',
#             'NO_TB_SCREENING']
# unsortedLabel.sort(key=keyorder.index)
# print (unsortedLabel)
#
#
#

labelsList = ['DEFAULT', 'MSM', 'PWID_SHARE', 'PWID_SHARE MSM', 'PWID_SHARE ' \
                                                                                                   'MSM ' \
                                                                                        'NO_VACCINE_B', 'PWID_SHARE '
                                                                                                        'MSM MIGRANT', 'PWID_SHARE MSM NO_VACCINE_B MIGRANT', 'PWID_SHARE MSM NO_VACCINE_B MIGRANT NO_TB_SCREENING', 'PWID_NO_SHARE', 'PWID_NO_SHARE MSM', 'PWID_NO_SHARE MSM NO_VACCINE_B', 'PWID_NO_SHARE MSM MIGRANT', 'PWID_NO_SHARE MSM NO_VACCINE_B MIGRANT', 'PWID_NO_SHARE MSM NO_VACCINE_B MIGRANT NO_TB_SCREENING', 'MIGRANT', 'MIGRANT NO_TB_SCREENING', 'MIGRANT NO_TB_SCREENING NO_VACCINE_B', 'MIGRANT MSM', 'MIGRANT MSM NO_TB_SCREENING', 'MIGRANT MSM NO_TB_SCREENING NO_VACCINE_B', 'MSM NO_VACCINE_B', 'MIGRANT MSM NO_VACCINE_B', 'MIGRANT NO_VACCINE_B', 'PWID_SHARE NO_VACCINE_B', 'PWID_SHARE MIGRANT', 'PWID_SHARE MIGRANT NO_TB_SCREENING', 'PWID_SHARE MIGRANT NO_VACCINE_B', 'PWID_SHARE MSM MIGRANT NO_TB_SCREENING', 'PWID_SHARE NO_VACCINE_B MIGRANT NO_TB_SCREENING', 'PWID_NO_SHARE NO_VACCINE_B', 'PWID_NO_SHARE MIGRANT', 'PWID_NO_SHARE MIGRANT NO_TB_SCREENING', 'PWID_NO_SHARE NO_VACCINE_B MIGRANT', 'PWID_NO_SHARE MSM MIGRANT NO_TB_SCREENING', 'PWID_NO_SHARE NO_VACCINE_B MIGRANT NO_TB_SCREENING']

# print(labelsList)

def read_json(fname):
    return json.load(open(fname, encoding="utf-8"))

answersRC = read_json("rcAnswers_it_backup29Nov.json")
#
# print(answersRC.keys())
#
obj_str = json.dumps(answersRC).replace("PWID_SHARE MSM", "MSM PWID_SHARE").replace("PWID_SHARE MSM NO_VACCINE_B ",
                                                                                    "MSM NO_VACCINE_B "
                                                                                    "PWID_SHARE").replace("PWID_SHARE MSM MIGRANT", "MIGRANT MSM PWID_SHARE").replace("PWID_SHARE MSM NO_VACCINE_B MIGRANT NO_TB_SCREENING", "MIGRANT MSM NO_TB_SCREENING NO_VACCINE_B PWID_SHARE").replace("PWID_NO_SHARE MSM", "MSM PWID_NO_SHARE").replace("PWID_NO_SHARE MSM NO_VACCINE_B", "MSM NO_VACCINE_B PWID_NO_SHARE" )

answersRCNew = json.loads(obj_str)
print("after replace", answersRCNew.keys())

with open('json_out_it_sorted.json', 'w') as json_file:
    json.dump(answersRCNew, json_file)

for element in labelsList:
    words = element.split()
    words.sort()
    print(words)

    # print(element)



# keyorder = ['HIV+', 'PARTNER_HIV+', 'PWID_SHARE', 'PWID_NO_SHARE', 'MSM', 'NO_VACCINE_B', 'MIGRANT', 'NO_TB_SCREENING']
# labelsListSorted = labelsList.sort(key=keyorder.index)
# print (labelsListSorted)
#