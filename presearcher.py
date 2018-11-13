import os
from time import mktime
from datetime import datetime
from random import shuffle

import feedparser

from model import PresearcherModel
from utils import ensure_dir, ensure_file, _read_file, _write_file, get_env_config


class PresearcherEnv(object):

    def __init__(self, config_file='~/.presearcher.json'):

        self.env_config = get_env_config(config_file)
        self.data_dir = self.get_data_dir()
        self.time_window = self.env_config.get('time_window', 14)

        # Easy access to commonly used files
        self.profiles_file_path = self.data_dir + 'profiles.json'
        ensure_file(self.profiles_file_path, [])
        self.subscriptions_file_path = self.data_dir + 'subscriptions.json'
        ensure_file(self.subscriptions_file_path, [])
        self.content_file_path = self.data_dir + 'content.json'
        ensure_file(self.content_file_path, {})

        self.model_data_dir = self.data_dir + 'model_data/'
        ensure_dir(self.model_data_dir)
        self.model = PresearcherModel(data_dir=self.model_data_dir)

    def get_data_dir(self):

        data_dir = self.env_config.get('data_dir')

        if '~' in data_dir:
            data_dir = os.path.expanduser(data_dir)

        if data_dir[-1] != '/':
            data_dir += '/'

        return data_dir

    def add_profile(self, profile_name):

        current_profiles = _read_file(self.profiles_file_path)

        new_profile = profile_name.lower().replace(' ', '-')

        if new_profile not in current_profiles:
            current_profiles.append(new_profile)
            _write_file(self.profiles_file_path, current_profiles)

            feedback_filename = '{base}feedback/{profile}.json'.format(
                                    base=self.data_dir, profile=profile_name)
            ensure_file(feedback_filename, [])

        else:
            raise ValueError('The profile {name} already exists!'.format(
                                name=new_profile))

    def add_feedback(self, profile_name, feedback_type, content):
        ''' Store feedback on suggested content
        content is a dictionary with all the relevant fields included
        feedback_type is either "pos" or "neg"
        '''

        feedback_filename = '{base}feedback/{profile}.json'.format(
                                    base=self.data_dir, profile=profile_name)
        ensure_file(feedback_filename, [])

        feedback = _read_file(feedback_filename)
        if feedback_type in ['pos', 'neg']:
            feedback.append({
                "label": feedback_type,
                "content": content
            })

        else:
            raise ValueError('Invalid Feedback Type {}'.format(feedback_type))

        _write_file(feedback_filename, feedback)

    def update_content(self):
        ''' Fetch Additional Content for all subscriptions
        Update the content file
        Remove content that is too old based on the time window
        '''

        current_content = _read_file(self.content_file_path)
        all_subscriptions = _read_file(self.subscriptions_file_path)

        print 'Updating Content'

        # Get updated content for every subscription
        for subscription in all_subscriptions:

            print 'updating subscription ' + subscription

            subscription_content = self.parse_feed(subscription)
            for item in subscription_content:

                if not item.get('link'):
                    print 'No Link!!!'
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
                print 'Item too Old!!!'
                old_content.append(item_id)

        for item in old_content:
            del current_content[item]

        # Write updated content to file
        _write_file(self.content_file_path, current_content)

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

            feed_items.append(parsed_item)

        return feed_items

    def rescore_all_profiles(self):
        # Do per-profile scoring on all fetched content

        profile_list = _read_file(self.profiles_file_path)

        for profile in profile_list:
            print('Rescoring profile {}'.format(profile))
            self.train_from_feedback(profile)
            self.rescore_profile(profile)

    def train_from_feedback(self, profile_name):
        # Train the model from the feedback received
        # Remove all previous training

        profile_list = _read_file(self.profiles_file_path)
        if profile_name not in profile_list:
            raise ValueError('Profile {} does not exist'.format(profile_name))

        feedback_filename = '{base}feedback/{profile}.json'.format(
                                    base=self.data_dir, profile=profile_name)
        try:
            training_content = _read_file(feedback_filename)
        except (OSError, IOError):
            raise ValueError('No Feedback file found for profile {}'.format(
                                profile_name))
        shuffle(training_content)

        self.model.train(training_content)
        print 'Successfully trained on {} examples'.format(
                len(training_content))

    def rescore_profile(self, profile_name):
        # Rescore the fetched content for a given profile

        full_content = _read_file(self.content_file_path)
        content_links, content_data = [], []

        for link, data in full_content.iteritems():
            content_links.append(link)
            content_data.append(data)

        new_content = {}

        predictions = self.model.predict(content_data)

        for prediction, link, content in zip(predictions, content_links, content_data):
            content.setdefault('profiles', {})
            content['profiles'][profile_name] = prediction['pos']
            new_content[link] = content

        _write_file(self.content_file_path, new_content)

    def get_top_content(self, profile_name):
        # Get top content for a specific profile

        all_content = _read_file(self.content_file_path)
        content_list = []

        for content_id, content_data in all_content.iteritems():

            profile_score = content_data.get('profiles', {}).get(profile_name, 0)
            if profile_score:
                content_list.append(content_data)

        sorted_content = sorted(content_list,
                                key=lambda k: k.get(
                                        'profiles', {}).get(
                                            profile_name, 0),
                                reverse=True)
        return sorted_content
