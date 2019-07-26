import gpt_2_simple as gpt2

def main():
    model_name = "117M"

    sess = gpt2.start_tf_sess()
    gpt2.finetune(sess,
                  'bestiary.json',
                  model_name=model_name,
                  run_name='dnd4',
                  steps=1000)   # steps is max number of training steps

    gpt2.generate(sess)

if __name__=='__main__': main()
