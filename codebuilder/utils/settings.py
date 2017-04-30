import os
import os.path

from codebuilder.utils import util

CONFIG_DIR = os.environ.get('CONFIG_DIR', '/etc/codebuilder')
CONFIG_FILES = []
LOG_LEVEL = 'debug'
LOG_DIR = '/var/log/orca'
LOG_INTERVAL = 6
LOG_INTERVAL_UNIT = 'h'
LOG_FORMAT = (
    '%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')
LOG_BACKUPS = 5
LOG_FILTERS=[]

config = util.load_configs([os.path.join(CONFIG_DIR, filename) for filename in CONFIG_FILES])
config_vars = vars()
for key, value in config.iteritems():
    config_vars[k] = value
for key, value in config_vars.items():
    if isinstance(value, util.ConfigAttr):
        config_vars[key] = parse(value)