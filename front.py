from flask import Flask, render_template 
from load_json import load
import json
import random
from generate_one import generate_one_with_name
import re

app = Flask(__name__, template_folder='templates')

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

@app.route("/")
def display():
    name = "The One Above All"
    monster = generate_one_with_name(name)
    monster = monster.replace("<|startoftext|>\n", "")
    
    tries = 3
    i = 0
    while i < tries:
        try: 
            result = json.loads(monster)
            break
        except json.decoder.JSONDecodeError as e:
            print(monster)
            print(e)
            errorpos = e.pos
            # might work occasionally
            addtok = '"'
            if "Expecting" in e.msg and 'delimiter' in e.msg: 
                addtok = re.match("Expecting '(*)' delimiter", e.msg).group(1)
            monster = monster[:errorpos] + '"' + monster[errorpos:]
            i += 1
    print(monster)
    # need a function to consolidate dupes
    # also find and convert unicode I guess; should be done in input thooo
    h = str(load(monster))
    
    # h = str(load(get_rand_json()))
    with open('templates/sb.html', 'w') as f: 
        f.write(h)
    return render_template('sb_addable.html')

if __name__ == '__main__': app.run()
