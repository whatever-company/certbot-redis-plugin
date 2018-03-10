import os
import sys
import tempfile

import pytest
SETTINGS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
sys.path.insert(0, SETTINGS_DIRECTORY)
from certbot_redis_plugin.plugin import Authenticator
import fakeredis
import mock

from certbot import achallenges, configuration

from certbot import constants

from certbot.tests import acme_util


class TestAuthPlugin(object):
    @mock.patch('redis.Redis', fakeredis.FakeRedis)
    def setup_method(self, method):
         # Setup fake redis for testing.
        self.r = fakeredis.FakeStrictRedis()
        self.name = 'certbot-redis-auth'
        self.name_cfg = self.name.replace('-', '_') + '_'
        self.tempdir = tempfile.mkdtemp(dir=tempfile.gettempdir())
        self.config = configuration.NamespaceConfig(
            mock.MagicMock(**constants.CLI_DEFAULTS)
        )
        self.config.verb = "certonly"
        self.config.config_dir = os.path.join(self.tempdir, 'config')
        self.config.work_dir = os.path.join(self.tempdir, 'work')
        self.config.logs_dir = os.path.join(self.tempdir, 'logs')
        self.config.cert_path = constants.CLI_DEFAULTS['auth_cert_path']
        self.config.fullchain_path = constants.CLI_DEFAULTS['auth_chain_path']
        self.config.chain_path = constants.CLI_DEFAULTS['auth_chain_path']
        self.config.server = "example.com"
        self.config.__setattr__(self.name_cfg + 'redis_url', "redis://test:42")
        self.subject = Authenticator(self.config, self.name)
        self.subject.redis_client = self.r
        self.http_chall = acme_util.ACHALLENGES[0] # Http Chall



    def teardown_method(self, method):
        self.r.flushall()


    def test_http_challenge_gets_saved_to_redis(self):
        self.subject._perform_single(self.http_chall)
        _, validation = self.http_chall.response_and_validation()
        assert self.r.get("ZXZhR3hmQURzNnBTUmIyTEF2OUlaZjE3RHQzanV4R0orUEN0OTJ3citvQQ") == validation