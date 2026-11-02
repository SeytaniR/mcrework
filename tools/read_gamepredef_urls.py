with open(r"mcgame\docs\client\predef\GamePredef.as", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

import re
for key in ["RES_URL_FOLDER", "RES_URL_WORD1", "RES_URL_WORD2", "RES_URL_EXT"]:
    m = text.find(key)
    if m != -1:
        print(text[m:m+250])
