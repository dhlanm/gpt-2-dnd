#!/bin/bash

mkdir tmp1
FLAGS="-g0 -I/usr/include:/usr/local/include -L/usr/lib:/usr/local/lib -wno-cpp -Wno-sign-compare -Wextra -Wall" CFLAGS="--std=c99" python3 -m pip install gpt_2_simple==0.5.3 bs4 --compile --no-cache-dir --global-option=build_ext --global-option="-j 4" -t tmp1

find tmp1 -name "*.so" | xargs strip
# find tmp1 -type f -name '*.py' -delete

mkdir libsgohere
cd libsgohere
mkdir lib
cp /usr/lib64/atlas/*.3 lib/.
# cp /usr/lib64/atlas/libptcblas.so.3 lib/.
# cp /usr/lib64/atlas/libatlas.so.3 lib/.
# cp /usr/lib64/atlas/libptf77blas.so.3 lib/.
# cp /usr/lib64/atlas/liblapack.so.3 lib/.
cp /usr/lib64/libgfortran.so.3 lib/.
cp /usr/lib64/libquadmath.so.0 lib/.
find . -name "*.so" | xargs strip
cd ..
cp /io/deeplearning2.zip /io/lambda.zip

cd tmp1
zip -r9 /io/lambda.zip *
cd ../libsgohere
zip -ur9 /io/lambda.zip lib/
