from front import fix_json
from load_json import load
import gpt_2_simple as gpt2

sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, run_name="dnd11")

for t in range(1, 11):
    pre_fix_exceptions = 0
    post_fix_exceptions = 0
    mons = 0
    temp = t / 10
    for i in range(10):
        mons = []
        with open('names.txt', 'r') as f: 
            line = f.readline()
            while line:
                mons.append(f'<|startoftext|>\n{{\n    "monster_name": "{line.strip()}"')
                line = f.readline()
        print(mons)
        monsters = gpt2.generate(sess, return_as_list=True, run_name="dnd11", batch_prefix=mons, temperature=temp, batch_size=len(mons), nsamples=len(mons), truncate="<|endoftext|>", length=10240)
        for mon in monsters: 
            mon = mon.replace("<|startoftext|>\n", "")
            try:
                h = str(load(mon))
            except: 
                pre_fix_exceptions += 1
            mon = fix_json(mon, 100)
            try: 
                h = str(load(mon))
            except: 
                post_fix_exceptions += 1
            print(len(mon))
            print(mon)
            mons += 1
        print(pre_fix_exceptions, post_fix_exceptions, mons)
    print('-'*40)
    print(pre_fix_exceptions, post_fix_exceptions, mons)
    print(f'{pre_fix_exceptions/mons * 100}% error pre fix at temperature {temp}')
    print(f'{post_fix_exceptions/mons * 100}% error post fix at temperature {temp}')
    print('-'*40)
