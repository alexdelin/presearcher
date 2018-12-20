import os
import shutil

from presearcher.environment import PresearcherEnv


TEST_CONFIG_FILE = 'config/presearcher-test.json'
TEST_DATA_DIR = 'test_data/'
TEST_PROFILES = ['foo', 'bar', 'baz']

# Clean out content from previous tests before starting
if os.path.exists(TEST_DATA_DIR):
    shutil.rmtree(TEST_DATA_DIR)

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

    def test_field_mappings(self):
        content = env.get_top_content(TEST_PROFILES[0])['content']
        for item in content:
            assert item.get('title')
            assert item.get('description')
            assert item.get('link')
            assert item.get('timestamp')
            score = item.get('score')
            assert isinstance(score, (float, int))
            assert score >= 0 and score <= 1
