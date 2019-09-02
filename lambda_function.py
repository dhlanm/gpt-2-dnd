from load_json import load
from generate_one import generate
import re
import os
import s3

sizes = ["T", "S", "M", "L", "H", "G"]
BUCKET_NAME = 'dnd-monster-code'
run_name = 'dnd11'

def download_model():
    s3 = boto3.resource('s3')
    if os.path.exists(os.cwd() + '/checkpoint'):
        # assume warm
        return
    os.mkdir('checkpoint')
    os.mkdir(f'checkpoint/{run_name}')
    bucket = s3.Bucket(BUCKET_NAME)
    for o in bucket.objects.filter(Prefix = 'checkpoint/{run_name}'):
        bucket.download_file(o.key, o.key)
    os.mkdir('models')
    os.mkdir('models/117M')
    for o in bucket.objects.filter(Prefix = 'models/117M'):
        bucket.download_file(o.key, o.key)


def generate_monster(prefix, temp=0.8):
    print(prefix)
    monster = generate(prefix, temperature=temp, truncate="<|endoftext|>")[0]
    monster = monster.replace("<|startoftext|>\n", "")
    
    tries = 100
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
                monster = monster[:errorpos] + addtok + monster[errorpos:]
            i += 1
    print(monster)
    # need a function to consolidate dupes
    # also find and convert unicode I guess; should be done in input thooo
    resp = {'json': monster}
    try:
        h = str(load(monster))
        resp['monster'] = h
    except Exception as e:
        resp['monster'] = f"<p>Error in monster creation: {e}</p>"
    return resp

def lambda_handler(event, context):
    print(event)
    download_model()
    name = event['name'] 
    temp = float(event.get('temp', '0.8'))
    prefix = f'<|startoftext|>\n{{\n    "monster_name": "{name}",\n'
    if event.get("size"):
        prefix += f'    "size": "{event["size"]}",\n'
    if event.get("type"): 
        if not event.get("size"): 
            prefix += f'    "size": "{random.choice(sizes)}",\n'
        prefix += f'    "type": "{event["type"]}",\n'
    return generate_monster(prefix, temp)

