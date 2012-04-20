#!/bin/sh

source ~/.virtualenvs/tendai/bin/activate

cd ~/code/tendai/server/tendai
./manage.py sms_send >> ~/sms.log
