import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open(r"mcgame\docs\client\utils\UrlUtil.as", 'r', encoding='utf-8', errors='ignore') as f:
    for i in range(25):
        print(f.readline().rstrip())
