#!/bin/bash -ex

export WORKSPACE=`pwd`
export PATH=$WORKSPACE/.env/bin:$PATH

# Setup virtualenv
if [ -d ".env" ]; then
    echo "**> virtualenv exists"
else
    echo "**> creating virtualenv"
    virtualenv .env --no-site-packages
fi

# Install dependencies
pip install -r server/deploy/requirements.txt

# Run tests
cd server/tendai
python manage.py test

