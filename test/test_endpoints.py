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


class TestEndpoints(object):
    """Test the actual REST API Endpoints do what they are supposed to"""

    def test_placeholder(self):
        assert True
