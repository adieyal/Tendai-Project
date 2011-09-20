#!/bin/bash -ex

export WORKSPACE=`pwd`
export PATH=$WORKSPACE/.env/bin:$PATH

cd bksmobi
ant debug

