import os

from presearcher.environment import PresearcherEnv


TEST_CONFIG_FILE = 'config/presearcher-test.json'
TEST_DATA_DIR = 'test_data/'
TEST_PROFILES = ['foo', 'bar', 'baz']
CONTENT_TO_CLEAN = [
    'content.json',
    'profiles.json',
    'subscriptions.json',
    'log/api.log',
    'feedback/foo.json',
    'feedback/bar.json',
    'feedback/baz.json'
]

# Clean out content from previous tests before starting
for item in CONTENT_TO_CLEAN:
    full_path = TEST_DATA_DIR + item
    if os.path.exists(full_path):
        os.remove(full_path)

env = PresearcherEnv(TEST_CONFIG_FILE)


class TestBasics(object):
    """Test basic function implementations of the library"""

    def test_env(self):
        assert isinstance(env, PresearcherEnv)

    def test_data_dir(self):
        assert env.data_dir == TEST_DATA_DIR

    def test_create_profile(self):
        assert env.get_profiles() == []

        for profile_name in TEST_PROFILES:
            env.add_profile(profile_name)

        assert env.get_profiles() == TEST_PROFILES

        for profile_name in TEST_PROFILES:
            assert os.path.exists('{base}feedback/{profile}.json'.format(
                                    base=TEST_DATA_DIR,
                                    profile=profile_name))

    def test_create_subscription(self):
        assert env.get_subscriptions() == []

        env.add_subscription('http://export.arxiv.org/rss/cs')
        assert env.get_subscriptions() == ['http://export.arxiv.org/rss/cs']

    def test_get_content_empty(self):
        assert env.get_top_content(TEST_PROFILES[0])['content'] == []

    def test_fetch_content(self):
        assert env.get_top_content(TEST_PROFILES[0])['content'] == []

        env.update_content()
        assert env.get_top_content(TEST_PROFILES[0])['content'] != []


class TestEndpoints(object):
    """Test the actual REST API Endpoints do what they are supposed to"""

    def test_placeholder(self):
        assert True
