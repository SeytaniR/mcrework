import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'mcgame\supabase\seeds\data_tbl_map.sql', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

for line in text.splitlines():
    line = line.strip()
    if line.startswith('('):
        parts = [p.strip().strip("'") for p in line.split(',')]
        if len(parts) >= 34:
            mid = parts[0].strip('(')
            if mid in ['1', '2', '3', '4', '5', '9', '22']:
                print(f"SQL Map {mid}: name={parts[21]}, height={parts[13]}, width={parts[33]}, safe=({parts[29]},{parts[30]})")
