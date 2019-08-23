cd dist
cp ../gpt_2_length_patch.py gpt_2_simple/gpt_2.pyi
cp ../biased_sampler.py gpt_2_simple/src/
cp ../generate_one.py .
cp ../lambda_function.py . 
cp ../load_json.py . 
cd ..
zip -gr build.zip build
aws s3 cp build.zip s3://dnd-monster-code/ --region us-east-1
aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:756054503873:function:generateMonster --s3-bucket s3://dnd-monster-code/ --region us-east-1
