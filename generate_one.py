import gpt_2_simple as gpt2
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, run_name="dnd5")
single_text = gpt2.generate(sess, return_as_list=True, run_name="dnd5", truncate="<|endoftext|>", prefix="<|startoftext|>", temperature= 0.8)[0]
# single_text = gpt2.generate(sess, return_as_list=True, run_name="dnd5", length=4000, prefix="<|startoftext|>", temperature=1.0)[0]
print(single_text)

