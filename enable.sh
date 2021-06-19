#!/bin/bash
option_headless=${1:-"1"}
cwd=$( dirname $0 )
cd $cwd
if [ ! -d .venv ];
then
    echo "Virtualenv is not installed"
    echo "Please check the README.md"
    exit 1
fi
source .venv/bin/activate
if [ ! -f env.ini ];
then
    echo "Script environment variables not founded"
    echo "Please check the README.md"
    exit 1
fi
source env.ini
export HEADLESS="${option_headless}"
python main.py enable
