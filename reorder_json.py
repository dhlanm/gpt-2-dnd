import json

def reorder(filename, indent):
    with open(f'{filename}.json') as f: 
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
        reordered['monster_name'] = reordered['monster_name'].strip()
        if indent > 0:
            new_text += f'<|startoftext|>\n{json.dumps(reordered, indent=indent)}\n<|endoftext|>\n'
        else:
            new_text += f'<|startoftext|>\n{json.dumps(reordered)}\n<|endoftext|>\n'
    with open(f'{filename}_{indent}_reordered.json', 'w') as f: 
        f.write(new_text)
def main():
    indent = 0
    reorder('homebrew', indent)
    reorder('bestiary', indent)
    print('done')

if __name__ == '__main__': main()
