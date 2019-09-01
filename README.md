# GPT-2 DND

Using minimaxir's gpt-2-simple with data from 5etools and D&D Beyond homebrew to generate new 5e monsters

### Running training

Your best bet is to use Google Colab, and mount your Drive. Then `%cd` into your Drive and train there, saving the model weights there. You can also just run locally if your GPU has enough memory to handle the model size, etc.

`git pull` the repository there, and `%cd` into it

Do `pip install gpt_2_simple -t . --no-deps` to install `gpt_2_simple` to the project repo

Run 

```
import gpt_2_simple as gpt2

model_name = "117M"
gpt2.download_gpt2(model_name=model_name)
```

to download the gpt-2 model. 

then
`!cp gpt_2_length_patch.py gpt_2_simple/gpt_2.py`
`!cp biased_sampler.py gpt_2_simple/src/`

The first patch is from [this pr](https://github.com/minimaxir/gpt-2-simple/blob/5053cf593e8738e04a0e3ae0d576868df4d611be/gpt_2_simple/gpt_2.py) Note it is heavily modified. It allows for gpt-2 to generate longer samples than the tensor size by using previous generated sample partials as context for later text.

The second patch allows for the model to sample from multiple sources with weights. For instance, 

```
model_name = "117M"
sess = gpt2.start_tf_sess()
gpt2.finetune(sess,
  ['bestiary.json', 'homebrew.json'],
  model_name=model_name,
  run_name='dnd11',
  steps=4000,
  dataset_probs = [0.7, 0.3])
```

will train the model for 4000 steps, pulling 70% from the 5etools bestiary, and 30% from the dndbeyond homebrew.

Then, to generate, you can run `python generate_one.py name` or use the `gpt2.generate` function directly like so:

```
name = "Batman"
gpt2.generate(sess, run_name="dnd11", prefix=f'<|startoftext|>\n{{\n    "monster_name": "{name}",\n', truncate="<|endoftext|>", length=10240, temperature=0.8, split_context=0.65)
```

### Running the webapp

If you want to run with nginx and wsgi, 
`cp dnd.service /etc/systemd/system/dnd.service`

`cp dnd_nginx /etc/nginx/sites-available/dnd`

Otherwise, just do `python front.py` and it will run a development Flask webserver locally. It is currently pointed at `./models/dnd11`

### D&D Beyond Scrape

The scraper tries to be polite, so it takes a few hours to finish. It grabs every homebrew monster with a rating of 1 or greater on dndbeyond and attempts to convert it from HTML to json with middling accuracy (the spellcasting blocks are usually screwed up at the moment, but most everything else seems to come through well enough).

The scraper caches everything, so once it's been run once it shouldn't be run again. 

### Stat block rendering

The [stat block rendering](https://github.com/Valloric/statblock5e) is not my own. A lot of attention to detail was put into that project and it's definitely worth checking out. 




#### THIS IS ALL VERY WIP 


#### TODO: 
fix dndbeyond spellcasting blocks as they are utterly broken

add sampling ability / multiple dataset ability to command line finetune

add instructions to front end

Run experiments with diff temps to estimate error rate (~20% but really not enough samples so do more)

revisit batch issue. Need the batch prefixes to be of exact same length and probably can't fix that, but might be able to fix weird whitespace in the original prefix...
PAD FRONT!

Add time elapsed measurement?

Definitely add a timeout at 5 minutes or so

Double column sheets!
data-two-column style="--data-content-height: 672px;"

domain lol
