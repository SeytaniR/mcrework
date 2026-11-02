with open(r"mcgame\docs\client\predef\GamePredef.as", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

m = text.find("RES_URL_WORD2[")
if m != -1:
    print(text[m:m+2500])
