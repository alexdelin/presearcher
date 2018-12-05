import os
from time import mktime
from datetime import datetime
from random import shuffle

import feedparser
import six

from presearcher.model import PresearcherModel
from presearcher.utils import ensure_dir, ensure_file, _read_file, \
                              _write_file, get_env_config, cleanup_title, \
                              validate_subscription_url


class PresearcherEnv(object):

    def __init__(self, logger=None, config_file='~/.presearcher.json'):

        if logger:
            self.log = logger
        else:
            #TODO Move instantiation to here and just
            pass

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

        self.log.info('Running App')

    def get_data_dir(self):

        data_dir = self.env_config.get('data_dir')

        if '~' in data_dir:
            data_dir = os.path.expanduser(data_dir)

        if data_dir[-1] != '/':
            data_dir += '/'

        return data_dir

    def get_profiles(self):

        profile_list = _read_file(self.profiles_file_path)
        return profile_list

    def get_subscriptions(self):

        subscriptions_list = _read_file(self.subscriptions_file_path)
        return subscriptions_list

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

    def add_subscription(self, subscription_url):

        current_subscriptions = _read_file(self.subscriptions_file_path)
        self.log.info('Adding subscription ' + subscription_url)

        if not validate_subscription_url(subscription_url):
            raise ValueError('Invalid Subscription URL')

        if subscription_url not in current_subscriptions:
            current_subscriptions.append(subscription_url)

        _write_file(self.subscriptions_file_path, current_subscriptions)

    def add_feedback(self, profile_name, feedback_type, content):
        ''' Store feedback on suggested content
        content is a dictionary with all the relevant fields included
        feedback_type is either "pos" or "neg"
        '''

        feedback_filename = '{base}feedback/{profile}.json'.format(
                                    base=self.data_dir, profile=profile_name)
        ensure_file(feedback_filename, {})

        feedback = _read_file(feedback_filename)

        if feedback_type in ['pos', 'neg']:
            feedback_element = {
                "label": feedback_type,
                "content": content
            }

            feedback_link = feedback_element['content']['link']

            if not feedback_link:
                raise ValueError('No Link found in Feedback Element {}'.format(
                    feedback_element['content']))

            if feedback_link in feedback.keys():
                '''Feedback already exists, check that the
                label is the same, otherwise replace it with the
                new label
                '''
                if feedback[feedback_link]['label'] == feedback_element['label']:
                    '''Labels Match. Do nothing because that
                    exact feedback already exists
                    '''
                    pass
                else:
                    # Labels do not Match, update it with the new feedback
                    feedback[feedback_link] = feedback_element
            else:
                feedback[feedback_link] = feedback_element

        else:
            raise ValueError('Invalid Feedback Type {}'.format(feedback_type))

        _write_file(feedback_filename, feedback)
        self.log.info('Added {feedback_type} feedback for '
                      'profile {profile_name}'.format(
                        feedback_type=feedback_type,
                        profile_name=profile_name))

    def update_content(self):
        ''' Fetch Additional Content for all subscriptions
        Update the content file
        Remove content that is too old based on the time window
        '''

        current_content = _read_file(self.content_file_path)
        all_subscriptions = _read_file(self.subscriptions_file_path)

        self.log.info('Updating Content')

        # Get updated content for every subscription
        for subscription in all_subscriptions:

            self.log.info('updating subscription ' + subscription)

            subscription_content = self.parse_feed(subscription)
            for item in subscription_content:

                if not item.get('link'):

                    self.log.warn('No Link in item {content}'.format(
                                    content=item))
                    continue

                if item['link'] not in current_content.keys():
                    current_content[item['link']] = item

        # Remove content that is too old
        old_content = []

        for item_id, item_content in six.iteritems(current_content):

            if item_id in ['last_fetched', 'last_scored']:
                continue

            item_pub = item_content.get('timestamp')
            pub_date = datetime.strptime(item_pub, '%Y-%m-%dT%H:%M:%S')
            time_elapsed = datetime.now() - pub_date
            days_elapsed = time_elapsed.days

            if days_elapsed >= self.time_window:
                self.log.info('Item too Old!!!')
                old_content.append(item_id)

        for item in old_content:
            del current_content[item]

        # Update Timestamp for Last Fetched Time
        current_timestamp = datetime.now().isoformat()[:19]
        current_content['last_fetched'] = current_timestamp

        # Write updated content to file
        _write_file(self.content_file_path, current_content)

    def parse_feed(self, feed_url):
        # Parse content from an external RSS Feed

        feed_items = []
        feed = feedparser.parse(feed_url)

        if feed.bozo or 'bozo_exception' in feed.keys():
            # Invalid feed Syntax detected by feedparser
            raise ValueError('Invalid feed data for URL ' + feed_url)

        for item in feed['items']:

            parsed_item = {
                "title": cleanup_title(item.get('title')),
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

        self.log.info('Updated Feed {url}'.format(url=feed_url))
        return feed_items

    def rescore_all_profiles(self):
        # Do per-profile scoring on all fetched content

        profile_list = _read_file(self.profiles_file_path)

        for profile in profile_list:

            self.log.info('Rescoring profile {}'.format(profile))

            error = self.train_from_feedback(profile)
            if error:
                self.log.warn('Got an error training from feedback '
                              'for profile {profile_name}'.format(
                                    profile_name=profile))
            else:
                self.rescore_profile(profile)

        self.update_last_scored_time()

    def update_last_scored_time(self):

        content = _read_file(self.content_file_path)
        content['last_scored'] = datetime.now().isoformat()[:19]

        _write_file(self.content_file_path, content)

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
            training_content = training_content.values()
        except (OSError, IOError):
            raise ValueError('No Feedback file found for profile {}'.format(
                                profile_name))
        shuffle(training_content)

        if not training_content:
            self.log.info('Skipping profile {profile_name} because it '
                          'has no training content'.format(
                                profile_name=profile_name))
            return True

        self.model.train(training_content)
        self.log.info('Successfully trained on {num} examples'.format(
                        num=len(training_content)))

        return False

    def rescore_profile(self, profile_name):
        # Rescore the fetched content for a given profile

        full_content = _read_file(self.content_file_path)
        content_links, content_data = [], []

        for link, data in six.iteritems(full_content):

            if link in ['last_fetched', 'last_scored']:
                continue

            content_links.append(link)
            content_data.append(data)

        new_content = {}

        predictions = self.model.predict(content_data)

        for prediction, link, content in zip(predictions, content_links, content_data):

            content.setdefault('profiles', {})
            content['profiles'][profile_name] = prediction['pos']
            new_content[link] = content

        # Add last fetched time back in
        new_content['last_fetched'] = full_content['last_fetched']

        _write_file(self.content_file_path, new_content)

    def get_top_content(self, profile_name, limit=20, start=0):
        # Get top content for a specific profile

        all_content = _read_file(self.content_file_path)
        content_list = []

        for content_id, content_data in six.iteritems(all_content):

            if content_id in ['last_scored', 'last_fetched']:
                continue

            content_data['score'] = content_data.get('profiles', {}).get(
                                                        profile_name, 0)
            content_data['score'] = round(content_data['score'], 2)

            if content_data.get('profiles'):
                del content_data['profiles']

            content_list.append(content_data)

        sorted_content = sorted(content_list,
                                key=lambda k: k.get(
                                        'score', 0),
                                reverse=True)

        if start > len(sorted_content):
            # Early exit for invalid start index
            return []

        if start + limit < len(sorted_content):
            sorted_content = sorted_content[start:start + limit]
        else:
            sorted_content = sorted_content[start:]

        top_content = {
            "last_fetched": all_content.get('last_fetched', ''),
            "last_scored": all_content.get('last_scored', ''),
            "content": sorted_content
        }

        return top_content
