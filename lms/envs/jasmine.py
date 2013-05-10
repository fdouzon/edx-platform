"""
This configuration is used for running jasmine tests
"""

from .test import *
from logsettings import get_logger_config

ENABLE_JASMINE = True
DEBUG = True

LOGGING = get_logger_config(TEST_ROOT / "log",
                            logging_env="dev",
                            tracking_filename="tracking.log",
                            dev_env=True,
                            debug=True,
                            local_loglevel='ERROR',
                            console_loglevel='ERROR',
                            analytics_provider = ANALYTICS_LOGGING_PROVIDER, 
                            analytics_enabled = MITX_FEATURES['ANALYTICS_LOGGING_ENABLED'], 
                            sns_timeout = ANALYTICS_SNS_TIMEOUT,
                            sns_topic = ANALYTICS_SNS_TOPIC, 
                            analytics_host = ANALYTICS_HTTP_HOST
                            )

PIPELINE_JS['js-test-source'] = {
    'source_filenames': sum([
        pipeline_group['source_filenames']
        for group_name, pipeline_group
        in sorted(PIPELINE_JS.items(), key=lambda item: item[1].get('test_order', 1e100))
        if group_name != 'spec'
    ], []),
    'output_filename': 'js/lms-test-source.js'
}

PIPELINE_JS['spec'] = {
    'source_filenames': sorted(rooted_glob(PROJECT_ROOT / 'static/', 'coffee/spec/**/*.js')),
    'output_filename': 'js/lms-spec.js'
}

JASMINE_TEST_DIRECTORY = PROJECT_ROOT + '/static/coffee'

STATICFILES_DIRS.append(COMMON_ROOT / 'test' / 'phantom-jasmine' / 'lib')

INSTALLED_APPS += ('django_jasmine', )
