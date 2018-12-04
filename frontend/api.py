#! /usr/bin/env/python

import json
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, render_template, send_from_directory

from presearcher.environment import PresearcherEnv
from presearcher.utils import log_request

app = Flask(__name__)

logger = logging.getLogger('presearcher_api')
logger.setLevel(logging.DEBUG)
log_handler = RotatingFileHandler('log/api.log', maxBytes=10000,
                                  backupCount=10)
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

env = PresearcherEnv(logger=logger)


# ----- UI + Web Content Routes -----


@app.route('/')
def select_profile():
    profile_list = env.get_profiles()
    log_request(request, logger)
    return render_template('select_profile.j2', profiles=profile_list)


@app.route('/viewer/<profile_name>')
def show_ui(profile_name):
    limit = request.args.get('limit', 20)
    start = request.args.get('start', 0)
    top_content = env.get_top_content(profile_name, limit, start)
    log_request(request, logger)
    return render_template('viewer.j2', profile_name=profile_name,
                           top_content=top_content)


@app.route('/new_profile')
def new_profile():
    log_request(request, logger)
    return render_template('new_profile.j2')


@app.route('/subscriptions', methods=['GET'])
def subscriptions():
    subscriptions = env.get_subscriptions()
    log_request(request, logger)
    return render_template('subscriptions.j2', subscriptions=subscriptions)


@app.route('/js/<path:path>', methods=['GET', 'POST'])
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>', methods=['GET', 'POST'])
def send_css(path):
    return send_from_directory('css', path)


@app.route('/img/<path:path>', methods=['GET', 'POST'])
def send_img(path):
    return send_from_directory('img', path)


# ----- Main Web App Routes -----


@app.route('/content/<profile_name>', methods=['GET'])
def get_content(profile_name):
    # Gets recommended content for a given profile
    limit = request.args.get('limit', 20)
    start = request.args.get('start', 0)
    top_content = env.get_top_content(profile_name, limit, start)
    log_request(request, logger)
    return json.dumps(top_content)


@app.route('/profiles', methods=['GET'])
def get_profiles():
    # Get names of all available Profiles
    log_request(request, logger)
    return json.dumps(env.get_profiles())


@app.route('/profiles', methods=['POST'])
def create_profile():
    # Create a new Profile
    profile_name = request.form.get('profile_name')
    env.add_profile(profile_name)
    log_request(request, logger)
    return 'Success'


@app.route('/subscriptions', methods=['POST'])
def new_subscription():
    new_subscription_url = request.form.get('url')
    env.add_subscription(new_subscription_url)
    log_request(request, logger)
    return 'Success'


@app.route('/feedback', methods=['GET', 'POST'])
def send_feedback():
    # Send feedback on a document
    request_data = request.get_json(force=True)

    profile_name = request_data.get('profile_name')
    feedback_type = request_data.get('feedback_type')
    content = json.loads(request_data.get('content', {}))

    if not profile_name or not feedback_type or not content:
        return 'ERROR, Missing Necessary Param'

    env.add_feedback(profile_name, feedback_type, content)

    log_request(request, logger)
    return 'Success!'


# ----- Administration Routes -----

@app.route('/fetch')
def fetch_content():
    # fetch updated content from all subscriptions
    env.update_content()
    log_request(request, logger)
    return 'Success!'


@app.route('/score', methods=['POST'])
def rescore():
    # fetch updated content from all subscriptions
    env.rescore_all_profiles()
    log_request(request, logger)
    return 'Success!'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
