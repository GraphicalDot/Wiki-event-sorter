#!/bin/bash

sudo apt-get -y install python-pip
sudo apt-get -y install git

#To install hunpos tagger for nltk
sudo apt-get -y install ocaml-nox
cd /home/ubuntu/time-line/trunk/
./build.sh build

sudo mv trunk/ /usr/local/bin/
cd ..
cp en_wsj.model /usr/local/bin
cd /home/ubuntu/time_line/
git clone https://github.com/grangier/python-goose.git
cd python-goose
pip install -r requirements.txt
python setup.py install
