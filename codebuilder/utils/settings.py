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
LOG_FILTERS = []

DATABASE_TYPE = 'mysql'
DATABASE_NAME = 'codebuilder'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'root'
DATABASE_HOST = 'localhost'
DATABASE_PORT = 3306
DATABASE_URI = util.LazyObj(
    lambda: '%s://%s:%s@%s:%s/%s' % (
        util.parse(DATABASE_TYPE),
        util.parse(DATABASE_USER),
        util.parse(DATABASE_PASSWORD),
        util.parse(DATABASE_HOST),
        util.parse(DATABASE_PORT),
        util.parse(DATABASE_NAME)
    )
)
DATABASE_POOL_TYPE = 'instant'

config = util.load_configs([
    os.path.join(CONFIG_DIR, filename) for filename in CONFIG_FILES
])
CONFIG_VARS = vars()
for key, value in config.iteritems():
    CONFIG_VARS[key] = value

LOG_LEVEL = util.Argument('--loglevel', dest='loglevel', default=LOG_LEVEL)
LOG_DIR = util.Argument('--logdir', dest='logdir', default=LOG_DIR)
LOG_FILE = util.Argument('--logfile', dest='logfile', default=LOG_FILE)
LOG_INTERVAL = util.Argument(
    '--log-interval', dest='log_interval', type=int, default=LOG_INTERVAL
)
LOG_INTERVAL_UNIT = util.Argument(
    '--log-interval_unit', dest='log_interval_unit',
    choices=['h', 'm', 'd'], default=LOG_INTERVAL_UNIT
)
LOG_FORMAT = util.Argument(
    '--log-format', dest='log_format', default=LOG_FORMAT
)
LOG_BACKUPS = util.Argument(
    '--log-backups', dest='log_backups', type=int, default=LOG_BACKUPS
)
LOG_FILTERS = util.Argument(
    '--log-filters', dest='log_filters', nargs='*', default=LOG_FILTERS
)
DATABASE_TYPE = util.Argument(
    '--database-type', dest='database_type', default=DATABASE_TYPE
)
DATABASE_NAME = util.Argument(
    '--database-name', dest='database_name', default=DATABASE_NAME
)
DATABASE_USER = util.Argument(
    '--database-user', dest='database_user', default=DATABASE_USER
)
DATABASE_PASSWORD = util.Argument(
    '--database-password', dest='database_password', default=DATABASE_PASSWORD
)
DATABASE_HOST = util.Argument(
    '--database-host', dest='database_host', default=DATABASE_HOST
)
DATABSE_PORT = util.Argument(
    '--database-port', dest='database_port', type=int, default=DATABASE_PORT
)
DATABASE_URI = util.Argument(
    '--database-uri', dest='database_uri', default=DATABASE_URI
)


def init_config():
    global CONFIG_VARS
    for key, value in CONFIG_VARS.items():
        if isinstance(value, util.ConfigAttr):
            CONFIG_VARS[key] = util.parse(value)
