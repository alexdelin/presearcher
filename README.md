# Presearcher
Simple ranking for new research based on your interests.

## Installation

Install Presearcher by running:
```bash
$ pip install -r requirements.txt
$ python setup.py develop
```

## Testing

To test the installation, move into the test folder and run `pytest`. If all of the tests pass, you are good to go.

```bash
$ cd test
$ pytest
```

## Setup

Before running presearcher, create your config file at `~/.presearcher.json`. You can create this by copying the sample version in `cofig/example_config.json` then editing the file as needed. 

```bash
$ cp config/example_config.json ~/.presearcher.json
```

This file stores the basic parameters about how presearcher operates, such as where it stores its data and how frequently it refershes data and retrains models.

## Usage

To run presearcher, move into the frontend folder and run the script `api.py`. This will start a flask app that runs on port `8080`. You can then access the web UI for presearcher from a browser.

```bash
$ cd frontend
$ python api.py
 * Serving Flask app "api" (lazy loading)
...
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```