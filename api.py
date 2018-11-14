#! /usr/bin/env/python

import json

from flask import Flask, request

from presearcher import PresearcherEnv

app = Flask(__name__)
env = PresearcherEnv()


# ----- Main Web App Routes -----

@app.route('/')
def show_ui():
    return 'The UI goes here!'


@app.route('/content/<profile_name>', methods=['GET'])
def get_content(profile_name):
    # Gets recommended content for a given profile
    limit = request.args.get('limit', 20)
    start = request.args.get('start', 0)
    top_content = env.get_top_content(profile_name, limit, start)
    return json.dumps(top_content)


@app.route('/profiles', methods=['GET'])
def get_profiles():
    # Get names of all available Profiles
    return json.dumps(env.get_profiles())


@app.route('/profiles', methods=['POST'])
def create_profile():
    # Create a new Profile
    profile_name = request.args.get('profile_name')
    env.add_profile(profile_name)
    return 'Success'


@app.route('/feedback', methods=['POST'])
def send_feedback():
    # Send feedback on a document
    request_data = request.get_json(force=True)

    profile_name = request_data.get('profile_name')
    feedback_type = request_data.get('feedback_type')
    content = request_data.get('content')

    env.add_feedback(profile_name, feedback_type, content)

    return 'Success!'


# ----- Administration Routes -----

@app.route('/fetch')
def fetch_content():
    # fetch updated content from all subscriptions
    env.update_content()
    return 'Success!'


@app.route('/score')
def rescore():
    # fetch updated content from all subscriptions
    env.rescore_all_profiles()
    return 'Success!'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
