import json
from collections import OrderedDict

def main():
    monsters = []
    with open('dndbeyond_scrape/dndbeyond.json') as f: 
        line = f.readline()
        while line: 
            if '<|startoftext|>' in line: 
                monster = ''
            elif '<|endoftext|>' in line:
                monster = OrderedDict(json.loads(monster))
                name = monster.pop("name")
                monster["monster_name"] = name
                monster.move_to_end("monster_name", last=False)

                trait = monster.pop("trait", None)
                action = monster.pop("action", None)
                if trait:
                    monster["name_pre_trait"] = monster["monster_name"]
                    monster["trait"] = trait
                if action:
                    monster["name_pre_action"] = monster["monster_name"]
                    monster["action"] = action
                monsters.append(monster)
            else: 
                monster += line
            line = f.readline()

    with open('homebrew.json', 'w') as outp:
        out_text = [json.dumps(m, indent=4) for m in monsters]
        out_text = '\n<|endoftext|>\n<|startoftext|>\n'.join(out_text)
        out_text = '<|startoftext|>\n' + out_text + '\n<|endoftext|>'
        outp.write(out_text)

if __name__ == '__main__': main()


    
