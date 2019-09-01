import gpt_2_simple as gpt2
import sys

run_name = "dnd11"

def generate(prefix="<|startoftext|>", length = None, truncate = "", temperature = 0.9, batch_size = 1, n_batches = 1):
    if not length and not truncate: 
        print("need one of length or truncate to generate")
        return
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, run_name=run_name)
    gen = gpt2.generate(sess, return_as_list=True, run_name=run_name, truncate=truncate, length=length, prefix=prefix, temperature=temperature, batch_size=batch_size, nsamples=batch_size*n_batches)
    return gen

def generate_from_list(prefixes, length=None, truncate="", temperature=0.9, batch_size=10, n_batches=1): 
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, run_name=run_name)
    gen = gpt2.generate(sess, return_as_list=True, run_name=run_name, truncate=truncate, length=length, batch_prefix=prefixes, temperature=temperature, batch_size=batch_size, nsamples=batch_size*n_batches)
    # print(gen) 
    print([len(g) for g in gen])
    print(gen[2])


def generate_one_with_name(name, temp=0.9): 
    pre = f'<|startoftext|>\n{{\n    "monster_name": "{name}",\n'
    single_text = generate(truncate="<|endoftext|>", prefix=pre, temperature=temp, length=None)[0]
    return single_text

def main():
    
    name = "Bob"

    if len(sys.argv) > 1: 
        name = sys.argv[1]
    pre = []
    with open('names.txt') as f: 
        l = f.readline()
        while l:
            pre.append(f'<|startoftext|>\n{{\n    "monster_name": "{l.strip()}",\n')
            l = f.readline()

    generate_from_list(truncate="<|endoftext|>", prefixes=pre)
    # print(generate_one_with_name(name))1


    # single_text = generate(truncate="<|endoftext|>", prefix="<|startoftext|>", temperature= 0.9, length=None)[0]
    # single_text = gpt2.generate(sess, return_as_list=True, run_name="dnd5", length=4000, prefix="<|startoftext|>", temperature=1.0)[0]
    # print(single_text)

if __name__ == '__main__': main()
