import os
import json
from time import mktime
from datetime import datetime

import feedparser


class PresearcherEnv(object):

    def __init__(self, config_file='~/.presearcher.json'):

        self.env_config = self.get_env_config(config_file)
        self.data_dir = self.get_data_dir()
        self.time_window = self.env_config.get('time_window', 14)

        # Easy access to commonly used files
        self.profiles_file_path = self.data_dir + 'profiles.json'
        self.ensure_file(self.profiles_file_path, [])
        self.subscriptions_file_path = self.data_dir + 'subscriptions.json'
        self.ensure_file(self.subscriptions_file_path, [])
        self.content_file_path = self.data_dir + 'content.json'
        self.ensure_file(self.content_file_path, {})

        self.model_cache = None

    def ensure_file(self, file_path, default_contents):

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        if not os.path.exists(file_path):
            with open(file_path, 'w') as file_object:
                json.dump(default_contents, file_object)

    def _read_file(self, file_path):

        with open(file_path, 'r') as file_object:
            contents = json.load(file_object)

        return contents

    def _write_file(self, file_path, file_contents):

        with open(file_path, 'w') as file_object:
            json.dump(file_contents, file_object)

    def get_env_config(self, config_location='~/.presearcher.json'):

        if '~' in config_location:
            config_location = os.path.expanduser(config_location)

        with open(config_location, 'r') as env_config_file:
            env_config = json.load(env_config_file)

        return env_config

    def get_data_dir(self):

        data_dir = self.env_config.get('data_dir')

        if '~' in data_dir:
            data_dir = os.path.expanduser(data_dir)

        if data_dir[-1] != '/':
            data_dir += '/'

        return data_dir

    def add_profile(self, profile_name):

        current_profiles = self._read_file(self.profiles_file_path)

        new_profile = profile_name.lower().replace(' ', '-')

        if new_profile not in current_profiles:
            current_profiles.append(new_profile)
            self._write_file(self.profiles_file_path, current_profiles)

        else:
            raise ValueError('The profile {name} already exists!'.format(
                                name=new_profile))

    def add_feedback(self, profile_name, feedback_type, content):
        # Store feedback on suggested content

        feedback_filename = self.data_dir + profile_name + '_feedback.json'
        self.ensure_file(feedback_filename, {"pos": [], "neg": []})

        feedback = self._read_file(feedback_filename)
        if feedback_type == 'pos':
            feedback['pos'].append(content)
        elif feedback_type == 'neg':
            feedback['neg'].append(content)
        else:
            raise ValueError('Invalid Feedback Type {}'.format(feedback_type))

    def update_content(self):
        # Fetch Additional Content for all subscriptions
        # Update the content file
        # Remove content that is too old based on the time window

        current_content = self._read_file(self.content_file_path)
        all_subscriptions = self._read_file(self.subscriptions_file_path)

        # Get updated content for every subscription
        for subscription in all_subscriptions:

            sub_content = self.parse_feed(subscription)
            for item in sub_content:

                if not item.get('link'):
                    continue

                if item['link'] not in current_content.keys():
                    current_content[item['link']] = item

        # Remove content that is too old
        old_content = []

        for item_id, item_content in current_content.iteritems():

            item_pub = item_content.get('timestamp')
            pub_date = datetime.strptime(item_pub, '%Y-%m-%dT%H:%M:%S')
            time_elapsed = datetime.now() - pub_date
            days_elapsed = time_elapsed.days

            if days_elapsed >= self.time_window:
                old_content.append(item_id)

        for item in old_content:
            del current_content[item]

        # Write updated content to file
        self._write_file(self.content_file_path, current_content)

    def parse_feed(self, feed_url):
        # Parse content from an external RSS Feed

        feed_items = []
        feed = feedparser.parse(feed_url)

        for item in feed['items']:

            parsed_item = {
                "title": item.get('title'),
                "description": item.get('summary'),
                "link": item.get('link')
            }

            if item.get('authors'):
                parsed_item["authors"] = [author['name'] for
                                          author in item.get('authors', [])]

            if item.get('published_parsed'):
                pub_datetime = datetime.fromtimestamp(
                                mktime(item['published_parsed']))
                parsed_item['timestamp'] = pub_datetime.strftime(
                                                '%Y-%m-%dT%H:%M:%S')
            else:
                parsed_item['timestamp'] = datetime.now().isoformat()[:19]

        return feed_items

    def score_fetched_content(self):
        # Do per-profile scoring on all fetched content

        profile_list = self._read_file(self.profiles_file_path)

        for profile in profile_list:
            self.train_from_feedback(profile)
            self.rescore_profile(profile)

    def train_from_feedback(self, profile_name):
        # Train the model from the feedback received
        # Remove all previous training
        pass

    def rescore_profile(self, profile_name):
        # Rescore the fetched content for a given profile
        pass

    def get_top_content(self, profile_name):
        # Get top content for a specific profile

        all_content = self._read_file(self.content_file_path)
        content_list = []
        profile_key = 'profile_{}'.format(profile_name)

        for content_id, content_data in all_content.iteritems():

            profile_score = content_data.get(profile_key)
            if profile_score:
                content_list.append(content_data)

        sorted_content = sorted(content_list, key=lambda k: k[profile_key])
        return sorted_content
