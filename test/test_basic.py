from presearcher.environment import PresearcherEnv


TEST_CONFIG_FILE = 'config/presearcher-test.json'
TEST_DATA_DIR = 'test_data/'


env = PresearcherEnv(TEST_CONFIG_FILE)


class TestBasics(object):
    """Testing for Presearcher Env"""

    def test_env(self):
        assert isinstance(env, PresearcherEnv)

    def test_data_dir(self):
        assert env.data_dir == TEST_DATA_DIR
