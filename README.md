using minimaxir's gpt-2-simple and data from 5etools to generate new 5e monsters

### Install 
Make sure you are on an environment with tensorflow 

Do `pip install gpt_2_simple -t . --no-deps` to install `gpt_2_simple` to this directory. You may also need to separately install its dependencies. 

You can also install `gpt_2_simple` whereever and just do the following two steps copying to your install directory.

Copy `gpt_2_length_patch.py` to `gpt_2_simple/gpt_2.py`

Copy `biased_sampler.py` to `gpt_2_simple/src/`


The `gpt_2_length_patch.py` is derived from the patch from this pr: `https://github.com/minimaxir/gpt-2-simple/blob/5053cf593e8738e04a0e3ae0d576868df4d611be/gpt_2_simple/gpt_2.py`. Note it is heavily modified. 

Also scraped dndbeyond for extra bestiary data. The scraper caches the files automatically.  Only scrapes monsters with score >= 1 for QC purposes. 

THIS IS ALL VERY WIP 


TODO: 
add another name param into json. ordered dict. (hold off on this for a bit)  

add sampling ability / multiple dataset ability to command line finetune

write a web parser to actually display generated JSON...
