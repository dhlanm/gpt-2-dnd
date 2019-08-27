using minimaxir's gpt-2-simple and data from 5etools to generate new 5e monsters

### Install 
Make sure you are on an environment with tensorflow 

Do `pip install gpt_2_simple -t . --no-deps` to install gpt_2_simple

then
`cp gpt_2_length_patch.py gpt_2_simple/gpt_2.py`
`cp biased_sampler.py gpt_2_simple/src/`

(the first patch is from this pr: https://github.com/minimaxir/gpt-2-simple/blob/5053cf593e8738e04a0e3ae0d576868df4d611be/gpt_2_simple/gpt_2.py) Note it is heavily modified. 

You'll also need to create or copy the model data. I should upload that to github...

Also, `cp dnd.service /etc/systemd/system/dnd.service`


Also scraped dndbeyond for extra bestiary data. The scraper caches the files automatically.  Only scrapes monsters with score >= 1 for QC purposes. 

THIS IS ALL VERY WIP 


TODO: 
fix dndbeyond spellcasting blocks as they are utterly broken

add sampling ability / multiple dataset ability to command line finetune

add info/instructions to front end

rewrite README to actually be helpful 

Run experiments with diff temps to estimate error rate (~20% but really not enough samples so do more)

revisit batch issue. Need the batch prefixes to be of exact same length and probably can't fix that, but might be able to fix weird whitespace in the original prefix...

Add time elapsed measurement?

Definitely add a timeout at 5 minutes or so

Switch to SSH geez

Double column sheets!
