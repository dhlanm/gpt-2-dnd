import json

def main():
    monsters = []
    with open('dndbeyond_scrape/dndbeyond.json') as f: 
        line = f.readline()
        while line: 
            if '<|startoftext|>' in line: 
                monster = ''
            elif '<|endoftext|>' in line:
                monster = json.loads(monster)
                trait = monster.pop("trait", None)
                action = monster.pop("action", None)
                if trait:
                    monster["name_pre_trait"] = monster["name"]
                    monster["trait"] = trait
                if action:
                    monster["name_pre_action"] = monster["name"]
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


    
