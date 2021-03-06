import os
import json
import re

import feedparser


def ensure_dir(dirname, logger=None):

    if not os.path.exists(dirname):
        if logger:
            logger.warn('Creating directory "{dirname}" '
                        'that does not exist'.format(
                            dirname=dirname))
        os.makedirs(dirname)


def ensure_file(file_path, default_contents, logger=None):

    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        if logger:
            logger.warn('Creating directory "{dirname}" '
                        'that does not exist'.format(
                            dirname=dirname))
        os.makedirs(dirname)

    if not os.path.exists(file_path):
        logger.warn('Creating file {file_path} that does not exist'.format(
                        file_path=file_path))
        with open(file_path, 'w') as file_object:
            json.dump(default_contents, file_object)


def _read_file(file_path):

    with open(file_path, 'r') as file_object:
        contents = json.load(file_object)

    return contents


def _write_file(file_path, file_contents):

    with open(file_path, 'w') as file_object:
        json.dump(file_contents, file_object)


def get_env_config(config_location='~/.presearcher.json'):

    if '~' in config_location:
        config_location = os.path.expanduser(config_location)

    with open(config_location, 'r') as env_config_file:
        env_config = json.load(env_config_file)

    return env_config


def cleanup_title(title):

    title = re.sub(string=title, pattern=r'\(arXiv:.*?\)', repl='')
    return title


def validate_subscription_url(url):

    parsed = feedparser.parse(url)

    if parsed.bozo or 'bozo_exception' in parsed.keys():
        # Invalid feed Syntax detected by feedparser
        return False

    return True


def log_request(request, logger):

    log_message = 'API Access - {method} {path}'.format(
                        method=request.method,
                        path=request.full_path)
    logger.info(log_message)
