from flask import Flask, render_template, Response, request 
from load_json import load
import json
import random
from generate_one import generate_one_with_name
import re

app = Flask(__name__, template_folder='static/templates')

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

def generate_monster(name):
    monster = generate_one_with_name(name)
    monster = monster.replace("<|startoftext|>\n", "")
    
    tries = 10
    i = 0
    while i < tries:
        try: 
            result = json.loads(monster)
            break
        except json.decoder.JSONDecodeError as e:
            print('attempted a fix: ') 
            print(monster)
            print(e)
            errorpos = e.pos
            # works sometimes since most errors are missing " or ",
            addtok = '"'
            print(e.msg)
            if "Extra data" in e.msg: 
                if errorpos == len(monster) - 1: 
                    monster = monster[:errorpos]
                else:
                    monster = monster[:errorpos] + monster[errorpos + 1:]
            else:
                if "Expecting" in e.msg and 'delimiter' in e.msg: 
                    addtok = re.match("Expecting '(.)' delimiter", e.msg).group(1)
                monster = monster[:errorpos] + '"' + monster[errorpos:]
            i += 1
    print(monster)
    # need a function to consolidate dupes
    # also find and convert unicode I guess; should be done in input thooo
    h = str(load(monster))
    return h

@app.route("/")
def index():
    content = render_template('index.html')
    return Response(content, mimetype="text/html")

@app.route("/create", methods=['POST'])
def create():
    name = request.json['name']
    return generate_monster(name)

@app.route("/old")
def display():
    name = "The One Above All"
    h = generate_monster(name)
    
    # h = str(load(get_rand_json()))
    with open('templates/sb.html', 'w') as f: 
        f.write(h)
    return render_template('sb_addable.html')

if __name__ == '__main__': app.run()
