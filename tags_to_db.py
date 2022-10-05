#!/usr/bin/env python

import re
import json

# fname = "RC_Answers_CK_10Sept.html"
fname = "RC_Answers_LT.html"

def remove_tags(tag_type, lst):
    """ Remove specific opening and closing tags from elements in lst
    :param tag_type: list with the type of tags to remove
    :param lst: the lst from which the tags of elements are to be removed
    """
    for ttype in tag_type:
        lst = list(map(lambda el: el.replace(
            "<{}>".format(ttype),"").replace(
                "</{}>".format(ttype), ""), lst))
    return lst

with open(fname, "r") as fp:
    rd = fp.read()
    h1s_lst = remove_tags(["h1", "strong"], re.findall(r"<h1>.*</h1>", rd))

    h1s_content_lst = remove_tags(["h1", "html"], re.findall(r"(?:</h1>[\s\S]*?<h1>)|(?:</h1>[\s\S]*</html>)", rd))

    for elm in [re.findall(r"(?:</h2>[\s\S]*?<h2>)|(?:</h2>[\s\S]*</h1>)|(?:</h2>[\s\S]*?$)", el) for el in h1s_content_lst]:
        print(len(elm))

    for elm in [re.findall(r"<h2>.*</h2>", el) for el in h1s_content_lst]:
        print("keys:", len(elm))
        print(elm)

    h2s_ps = [dict(zip(remove_tags(["h2"], re.findall(r"<h2>.*</h2>", el)),
              remove_tags(["h2"], re.findall(r"(?:</h2>[\s\S]*?<h2>)|(?:</h2>[\s\S]*</h1>)|(?:</h2>[\s\S]*?$)", el)))) for el in h1s_content_lst]

    # for el in h2s_ps:
    #     print(el.keys())

    h1_h2_main = dict(zip(h1s_lst, h2s_ps))
    #
    # for el in h1_h2_main:
    #     print(el)
    #     for v in h1_h2_main[el]:
    #         print(v)
    #         print(len(v))

    with open("rcAnswers_lt.json", "w") as jfp:
        json.dump(h1_h2_main, jfp)

    # for el in h1s_content_lst:
    #     = map(lambda el: el.replace("<h2>","").replace("</h1>", ""),re.findall(r"<h2>[\S]*</h2>", rd))
    #
    # h2_lst = re.findall(, r"<h2>/S</h2>")
    # ps_lst = re.findall(r"</h2>/S<h2>")
    # ans = re.sub(r"Answer \d{1,3}", re.sub(r"<h1>.*</h1>"))
