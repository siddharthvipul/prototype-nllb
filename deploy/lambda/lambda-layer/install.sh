rm -rf python
rm -rf venv8

python3.8 -m venv ./venv8
source ./venv8/bin/activate
pip install -r requirements.txt --no-cache-dir --platform=manylinux2014_x86_64 --only-binary=:all: --target ./venv8/lib/python3.8/site-packages

mkdir python
cp -r venv8/lib/python3.8/site-packages/ python/
zip -r layer_content.zip python

rm -rf python
rm -rf venv8