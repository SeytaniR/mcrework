import os

for root, dirs, files in os.walk('mcgame'):
    for file in files:
        if file.endswith('.as'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f_in:
                content = f_in.read()
                if 'effect' in content.lower() and ('skill' in content.lower() or 'battle' in content.lower()):
                    for line in content.splitlines():
                        if any(k in line.lower() for k in ['resource/effect', 'resource/skill', 'skill_effect', 'geteffect', 'effecturl', 'loadskill', 'loadeffect']):
                            print(f'{file}: {line.strip()[:140]}')
