from flask import Flask, render_template 
from load_json import load
import json
import random

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
    # i have no idea what i'm doing
    h = str(load(get_rand_json()))
    with open('templates/sb.html', 'w') as f: 
        f.write(h)
    return render_template('sb_addable.html')

if __name__ == '__main__': app.run()
