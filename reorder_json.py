import json

with open('homebrew.json') as f: 
# with open('bestiary_new.json') as f: 
    text = f.read().split('<|endoftext|>\n<|startoftext|>\n')
    text[0] = '\n'.join(text[0].split('\n')[1:])
    text[-1] = '\n'.join(text[-1].split('\n')[:-1]).replace('<|endoftext|>','')

start = ['monster_name', 'type', 'cr', 'size', 'alignment', 'speed', 'str', 'dex', 'con', 'int', 'wis', 'cha', 'ac', 'hp']
new_text = ''
for monster in text: 
    m = json.loads(monster)
    keys = list(m.keys())
    end = [x for x in keys if x not in start]
    order = start + end
    if 'cr' not in m: 
        m['cr'] = '-'
    if 'alignment' not in m: 
        m['alignment'] = ['A'] 
    reordered = {k: m[k] for k in order}
    new_text += f'<|startoftext|>\n{json.dumps(reordered, indent=1)}\n<|endoftext|>\n'
with open('homebrew_reordered.json', 'w') as f: 
# with open('bestiary_reordered.json', 'w') as f: 
    f.write(new_text)
    
