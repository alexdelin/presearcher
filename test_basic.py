from presearcher import PresearcherEnv

env = PresearcherEnv()


class TestClass(object):
    """Testing for Presearcher Env"""

    def test_env(self):
        assert isinstance(env, PresearcherEnv)
