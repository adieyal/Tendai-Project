#!/bin/bash

HOME=/home/sarpam

source ${HOME}/.virtualenvs/tendai/bin/activate
export LD_LIBRARY_PATH=${HOME}/lib

cd ${HOME}/code/tendai/server/tendai
/home/sarpam/.virtualenvs/tendai/bin/python ./manage.py sms_send --settings=tendai.settings_siteone
