import gpt_2_simple as gpt2

def main():
    model_name = "117M"

    sess = gpt2.start_tf_sess()
    gpt2.finetune(sess,
                  ['bestiary.json', 'dndbeyond_scrape/dndbeyond.json'],
                  model_name=model_name,
                  run_name='dndtestdelete',
                  steps=5000,
                  dataset_probs = [0.7, 0.3])   # steps is max number of training steps

    gpt2.generate(sess)

if __name__=='__main__': main()
