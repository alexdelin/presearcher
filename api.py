#! /usr/bin/env/python

from flask import Flask, request

from presearcher import PresearcherEnv

app = Flask(__name__)
env = PresearcherEnv()


@app.route('/')
def show_ui():
    return 'The UI goes here!'


@app.route('/content/<profile:profile>', methods=['GET'])
def get_content(profile):
    # Gets recommended content for a given profile
    return []


@app.route('/profiles', methods=['GET'])
def get_profiles():
    # Get names of all available Profiles
    return env.get_profiles()


@app.route('/profiles', methods=['POST'])
def create_profile():
    # Create a new Profile
    profile_name = request.args.get('profile_name')
    env.add_profile(profile_name)
    return 'Success'


@app.route('/feedback')
def send_feedback():
    # Send feedback on a document
    request_data = request.get_json(force=True)

    profile_name = request_data('profile_name')
    feedback_type = request_data('feedback_type')
    content = request_data.get('content')

    env.add_feedback(profile_name, feedback_type, content)

    return 'Success'
