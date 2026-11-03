import sys, re

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

with open("mcgame/supabase/seeds/data_tbl_map.sql", "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

# Let's find the values block after INSERT INTO ... VALUES
val_pos = sql.find("VALUES")
if val_pos != -1:
    values_str = sql[val_pos + 6:]
    # parse row by row: each row starts with '(' and ends with ')' followed by ',' or ';'
    # we can tokenize character by character
    rows = []
    cur_row = []
    in_paren = False
    in_quote = False
    i = 0
    while i < len(values_str):
        c = values_str[i]
        if not in_quote:
            if c == "'":
                in_quote = True
                cur_row.append(c)
            elif c == '(':
                in_paren = True
                cur_row = []
            elif c == ')':
                in_paren = False
                rows.append("".join(cur_row))
                cur_row = []
            elif in_paren:
                cur_row.append(c)
        else:
            if c == "'":
                if i + 1 < len(values_str) and values_str[i+1] == "'":
                    cur_row.append("''")
                    i += 1
                else:
                    in_quote = False
                    cur_row.append(c)
            else:
                cur_row.append(c)
        i += 1

    print(f"Total rows parsed properly: {len(rows)}")
    for idx, r in enumerate(rows[:5]):
        # parse fields
        fields = []
        cur_fld = []
        in_q = False
        j = 0
        while j < len(r):
            ch = r[j]
            if not in_q:
                if ch == "'":
                    in_q = True
                elif ch == ',':
                    fields.append("".join(cur_fld).strip())
                    cur_fld = []
                else:
                    cur_fld.append(ch)
            else:
                if ch == "'":
                    if j + 1 < len(r) and r[j+1] == "'":
                        cur_fld.append("'")
                        j += 1
                    else:
                        in_q = False
                else:
                    cur_fld.append(ch)
            j += 1
        fields.append("".join(cur_fld).strip())
        print(f"Row {idx+1}: id={fields[0]}, name={fields[21]}, width={fields[33]}, height={fields[13]}, fields_count={len(fields)}")
