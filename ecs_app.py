  
from starlette.applications import Starlette
from starlette.responses import UJSONResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles
import gpt_2_simple as gpt2
import uvicorn
import os
from generate_one import generate
import json
import sys
import re
import traceback

application = Starlette(debug=False)

run_name = "dnd14"

response_header = {
    'Access-Control-Allow-Origin': '*'
}

sess = gpt2.start_tf_sess(threads=1)
gpt2.load_gpt2(sess, run_name=run_name)

sizes = ["T", "S", "M", "L", "H", "G"]

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
    monster = generate(sess, prefix, temperature=temp, truncate="<|endoftext|>", length=10240)[0]
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

@application.route('/create', methods=['POST'])
async def homepage(request):

    params = await request.form()

    name = params['name']
    temp = float(params.get('temp', '0.8'))
    if name:
        prefix = f'<|startoftext|>\n{{\n    "monster_name": "{name}",\n'
        if params.get("size"):
            prefix += f'    "size": "{params["size"]}",\n'
        if params.get("type"):
            if not params.get("size"):
                prefix += f'    "size": "{random.choice(sizes)}",\n'
            prefix += f'    "type": "{params["type"]}",\n'
    else:
        prefix = f'<|startoftext|>\n{{\n'
    monster = generate_monster(prefix, temp)
    sys.stderr.write(monster)
    # response = UJSONResponse({'text': monster}, headers=response_header)
    response = PlainTextResponse(monster, headers=response_header)
    sys.stderr.write(str(response))
    return response

# app.mount('/', StaticFiles(directory='build', html=True), name='static')

if __name__ == '__main__':
    uvicorn.run(application, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
