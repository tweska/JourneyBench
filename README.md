# JourneyBench


## Setup

Install the required packages:
```shell
$ apt install python3.11 python3.11-venv
$ apt install protobuf-compiler
```

Initialize the Python virtual environment:
```shell
$ python3.11 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

Before you can run any of the tools you must run the following commands (in the root directory of the project):
```shell
$ source env/bin/activate
$ export PYTHONPATH=$PWD
```
