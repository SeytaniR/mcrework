for fn in ['web/style.css', 'web/main.js']:
    with open(fn, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n')
    with open(fn, 'wb') as f:
        f.write(content)
print("Normalized style.css and main.js to \\n")
