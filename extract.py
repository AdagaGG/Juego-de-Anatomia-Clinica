import json
import re

def extract_database():
    with open('script.js', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find the baseDeDatos array
    match = re.search(r'const baseDeDatos = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("Could not find baseDeDatos!")
        return

    array_str = match.group(1)
    
    # Javascript object literal to JSON string
    # Try to quote unquoted keys
    array_str = re.sub(r'([{,]\s*)([a-zA-Z_]\w*)\s*:', r'\1"\2":', array_str)
    
    # Convert single quotes to double quotes for strings if possible
    # but eval handles single quotes fine.
    
    # Clean up any trailing commas
    json_str = re.sub(r',\s*\}', '}', array_str)
    json_str = re.sub(r',\s*\]', ']', json_str)
    
    py_dict_str = json_str.replace('true', 'True').replace('false', 'False')
    
    # But wait, python's eval might just work if we replace true/false
    # Actually, let's just use Python's eval to parse it as a dict list!
    
    py_dict_str = array_str.replace('true', 'True').replace('false', 'False')
    # Because of single quotes, it's valid python!
    try:
        db = eval(py_dict_str)
        with open('database.py', 'w', encoding='utf-8') as out:
            out.write("base_de_datos = [\n")
            for item in db:
                out.write("  {\n")
                for k, v in item.items():
                    if isinstance(v, str):
                        out.write(f'    "{k}": {repr(v)},\n')
                    else:
                        out.write(f'    "{k}": {v},\n')
                out.write("  },\n")
            out.write("]\n")
        print(f"Successfully extracted {len(db)} questions to database.py")
    except Exception as e:
        print("Eval failed:", e)

if __name__ == '__main__':
    extract_database()
