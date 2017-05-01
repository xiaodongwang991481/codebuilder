import os
import os.path

from codebuilder.utils import util

CONFIG_DIR = os.environ.get('CONFIG_DIR', '/etc/codebuilder')
CONFIG_FILES = []
LOG_LEVEL = 'debug'
LOG_DIR = '/var/log/codebuilder'
LOG_FILE = None
LOG_INTERVAL = 6
LOG_INTERVAL_UNIT = 'h'
LOG_FORMAT = (
    '%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')
LOG_BACKUPS = 5
LOG_FILTERS=[]

config = util.load_configs([os.path.join(CONFIG_DIR, filename) for filename in CONFIG_FILES])
CONFIG_VARS = vars()
for key, value in config.iteritems():
    CONFIG_VARS[k] = value

LOG_LEVEL = util.Argument('--loglevel', dest='loglevel', default=LOG_LEVEL)
LOG_DIR = util.Argument('--logdir', dest='logdir', default=LOG_DIR)
LOG_FILE = util.Argument('--logfile', dest='logfile', default=LOG_FILE)
LOG_INTERVAL = util.Argument('--log_interval', dest='log_interval', type=int, default=LOG_INTERVAL)
LOG_INTERVAL_UNIT = util.Argument('--log_interval_unit', dest='log_interval_unit', choices=['h', 'm', 'd'], default=LOG_INTERVAL_UNIT)
LOG_FORMAT = util.Argument('--log_format', dest='log_format', default=LOG_FORMAT)
LOG_BACKUPS = util.Argument('--log_backups', dest='log_backups', type=int, default=LOG_BACKUPS)
LOG_FILTERS = util.Argument('--log_filters', dest='log_filters', nargs='*', default=LOG_FILTERS)

def init_config():
    global CONFIG_VARS
    for key, value in config_vars.items():
        if isinstance(value, util.ConfigAttr):
            CONFIG_VARS[key] = parse(value)
