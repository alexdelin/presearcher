import os

from presearcher.environment import PresearcherEnv


TEST_CONFIG_FILE = 'config/presearcher-test.json'
TEST_DATA_DIR = 'test_data/'
CONTENT_TO_CLEAN = [
    'content.json',
    'profiles.json',
    'subscriptions.json'
]

# Clean out content from previous tests before starting
for item in CONTENT_TO_CLEAN:
    full_path = TEST_DATA_DIR + item
    if os.path.exists(full_path):
        os.remove(full_path)

env = PresearcherEnv(TEST_CONFIG_FILE)


class TestBasics(object):
    """Testing for Presearcher Env"""

    def test_env(self):
        assert isinstance(env, PresearcherEnv)

    def test_data_dir(self):
        assert env.data_dir == TEST_DATA_DIR

    def test_create_profile(self):
        assert env.get_profiles() == []

        env.add_profile('john')
        assert env.get_profiles() == ['john']

        assert os.path.exists(TEST_DATA_DIR + 'feedback/john.json')

    def test_create_subscription(self):
        assert env.get_subscriptions() == []

        env.add_subscription('http://export.arxiv.org/rss/cs')
        assert env.get_subscriptions() == ['http://export.arxiv.org/rss/cs']
