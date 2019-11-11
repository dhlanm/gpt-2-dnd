from flask import Flask, render_template, Response, request 
import json
import random
from generate_one import generate
import re
import traceback
import os

app = Flask(__name__, static_folder="build")
sizes = ["T", "S", "M", "L", "H", "G"]

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


def get_rand_json(): 
    monsters = []
    with open('bestiary.json', 'r') as f: 
        line = f.readline()
        while line: 
            if '<|startoftext|>' in line: 
                monster = ''
            elif '<|endoftext|>' in line:
                monsters.append(json.loads(monster))
            else: 
                monster += line
            line = f.readline()
    return random.choice(monsters)

def fix_json(monster, tries):
    i = 0
    while i < tries:
        try: 
            result = json.loads(monster)
            break
        except json.decoder.JSONDecodeError as e:
            # print('attempted a fix: ') 
            # print(monster)
            # print(e)
            errorpos = e.pos
            # works sometimes since most errors are missing " or ",
            addtok = '"'
            # print(e.msg)
            if "Extra data" in e.msg: 
                if errorpos == len(monster) - 1: 
                    monster = monster[:errorpos]
                else:
                    monster = monster[:errorpos] + monster[errorpos + 1:]
            else:
                if "Expecting" in e.msg and 'delimiter' in e.msg: 
                    addtok = re.match("Expecting '(.)' delimiter", e.msg).group(1)
                monster = monster[:errorpos] + addtok + monster[errorpos:]
            i += 1
    return monster


def generate_monster(prefix, temp=0.8):
    print(prefix)
    monster = generate(prefix=prefix, temperature=temp, truncate="<|endoftext|>", length=10240)[0]
    monster = monster.replace("<|startoftext|>\n", "")
    f_monster = fix_json(monster, 100)
    print(f_monster)
    # need a function to consolidate dupes
    # also find and convert unicode I guess; should be done in input thooo
    resp = f_monster
    try:
        json.loads(f_monster)
    except Exception as e:
        traceback.print_exc()
        resp = monster
    return resp

@app.route("/create", methods=['POST'])
def create():
    print(request.form)
    name = request.form['name'] 
    temp = float(request.form.get('temp', '0.8'))
    if name:
        prefix = f'<|startoftext|>\n{{\n    "monster_name": "{name}",\n'
        if request.form.get("size"):
            prefix += f'    "size": "{request.form["size"]}",\n'
        if request.form.get("type"): 
            if not request.form.get("size"): 
                prefix += f'    "size": "{random.choice(sizes)}",\n'
            prefix += f'    "type": "{request.form["type"]}",\n'
    else:
        prefix = f'<|startoftext|>\n{{\n'
    return generate_monster(prefix, temp)

if __name__ == '__main__': 
    app.run(host='0.0.0.0', debug=True, threaded=True, port=80) #DO NOT PUSH :)
