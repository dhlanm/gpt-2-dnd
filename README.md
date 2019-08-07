using minimaxir's gpt-2-simple and data from 5etools to generate new 5e monsters

### Install 
Make sure you are on an environment with tensorflow 

Do `pip install gpt_2_simple -t . --no-deps` to install gpt_2_simple


to use generate_one.py you should use the special gpt_2.py 
(the patch from this pr: https://github.com/minimaxir/gpt-2-simple/blob/5053cf593e8738e04a0e3ae0d576868df4d611be/gpt_2_simple/gpt_2.py) Note it is heavily modified. 

Also scraped dndbeyond for extra bestiary data. The scraper caches the files automatically.  Only scrapes monsters with score >= 1 for QC purposes. 

THIS IS ALL VERY WIP 


TODO: 
fix dndbeyond spellcasting blocks as they are utterly broken

add sampling ability / multiple dataset ability to command line finetune

refactor JSON display; hook it up to generation
