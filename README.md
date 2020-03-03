# GPT-2 DND

Using minimaxir's gpt-2-simple (0.5.4 guaranteed to work) with data from 5etools and D&D Beyond homebrew to generate new 5e monsters

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

Best bet would be to run with docker-compose

First, get the [frontend](github.com/dhlanm/gpt-2-dnd-frontend), build it, and run `docker build -t gpt-2-dnd-frontend .`

Then, in this directory, run `docker build -t gpt-2-dnd .`

Then, `docker-compose up -d`

At this point, you will be up and running. Of course, you'll need a trained model for it to do very much. Right now, the web app (`ecs_app.py`) is pointed at `/models/dnd14`. 

### D&D Beyond Scrape

The scraper tries to be polite, so it takes a few hours to finish. It grabs every homebrew monster with a rating of 1 or greater on dndbeyond and attempts to convert it from HTML to json with middling accuracy (the spellcasting blocks are usually screwed up at the moment, but most everything else seems to come through well enough).

The scraper caches everything, so once it's been run once it shouldn't be run again. 

### React app

The frontend react app at github.com/dhlanm/gpt-2-dnd-frontend is developed by github.com/el1t. Huge props to him for creating an absolutely beautiful interface. 


#### TODO: 
add sampling ability / multiple dataset ability to command line finetune

add instructions to front end

Run experiments with diff temps to estimate error rate (~20% but really not enough samples so do more)

revisit batch issue. Need the batch prefixes to be of exact same length and probably can't fix that, but might be able to fix weird whitespace in the original prefix...
PAD FRONT!
looks like batch mode just doesn't work properly. really weird generation when you do things with it though...

Add time elapsed measurement?

Definitely add a timeout at 5 minutes or so

Revisit training, using less whitespace / tokens to signify whitespace while reducing overall character count. 

Revisit training, reordering the stat sheet so more interesting items can go first (would have to change frontend design slightly perhaps?)
