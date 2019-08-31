from flask import Flask, render_template, Response, request 
from load_json import load
import json
import random
from generate_one import generate
import re
from gevent.pywsgi import WSGIServer

app = Flask(__name__, template_folder='static/templates')
sizes = ["T", "S", "M", "L", "H", "G"]

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
    monster = generate(prefix, temperature=temp, truncate="<|endoftext|>", length=20480)[0]
    monster = monster.replace("<|startoftext|>\n", "")
    f_monster = fix_json(monster, 100)
    print(f_monster)
    # need a function to consolidate dupes
    # also find and convert unicode I guess; should be done in input thooo
    resp = {'json':f_monster}
    try:
        h = str(load(f_monster))
        resp['monster'] = h
    except Exception as e:
        try: 
            h = str(load(monster))
            resp['monster'] = h #won't happen, just getting original error here
        except Exception as e: 
            resp['monster'] = f"<p>Error in monster creation: {e}</p>"
        resp['json'] = monster
    return resp

@app.route("/")
def index():
    content = render_template('index.html')
    return Response(content, mimetype="text/html")

@app.route("/create", methods=['POST'])
def create():
    print(request.json)
    name = request.json['name'] 
    temp = float(request.json.get('temp', '0.8'))
    prefix = f'<|startoftext|>\n{{\n    "monster_name": "{name}",\n'
    if request.json.get("size"):
        prefix += f'    "size": "{request.json["size"]}",\n'
    if request.json.get("type"): 
        if not request.json.get("size"): 
            prefix += f'    "size": "{random.choice(sizes)}",\n'
        prefix += f'    "type": "{request.json["type"]}",\n'
    return generate_monster(prefix, temp)

if __name__ == '__main__': 
    app.run(host='0.0.0.0', debug=True, threaded=True)
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()
