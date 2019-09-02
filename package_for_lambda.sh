mkdir build
cp deeplearning-bundle.zip build.zip
cd build
FLAGS="-g0 -I/usr/include:/usr/local/include -L/usr/lib:/usr/local/lib -wno-cpp -Wno-sign-compare -Wextra -Wall" CFLAGS="--std=c99" python3 -m pip install gpt_2_simple==0.5.3 bs4 --compile --no-cache-dir --global-option=build_ext --global-option="-j 4" -t .
find . -name "*.so" | xargs strip

cp ../gpt_2_length_patch.py gpt_2_simple/gpt_2.py
cp ../biased_sampler.py gpt_2_simple/src/
cp ../generate_one.py .
cp ../lambda_function.py . 
cp ../load_json.py . 
zip -gr ../build.zip *
cd ..
aws s3 cp build.zip s3://dnd-monster-code/ --region us-east-1
aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:756054503873:function:generateMonster --s3-bucket s3://dnd-monster-code/ --region us-east-1
