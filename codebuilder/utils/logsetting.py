import logging
import logging.handlers
import os
import os.path
import sys

from codebuilder.utils import util
from codebuilder.utils import settings

# mapping str setting in flag --loglevel to logging level.
LOGLEVEL_MAPPING = {
    'finest': logging.DEBUG - 2,  # more detailed log.
    'fine': logging.DEBUG - 1,    # detailed log.
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


logging.addLevelName(LOGLEVEL_MAPPING['fine'], 'fine')
logging.addLevelName(LOGLEVEL_MAPPING['finest'], 'finest')


# disable logging when logsetting.init not called
logging.getLogger().setLevel(logging.CRITICAL)


def getLevelByName(level_name):
    """Get log level by level name."""
    return LOGLEVEL_MAPPING[level_name]


def init_logging(
        logfile=setting.LOG_FILE,
        logdir=settings.LOG_DIR,
        loglevel=settings.LOG_LEVEL,
        log_interval_unit=settings.LOG_INTERVAL_UNIT,
        log_interval=settings.LOG_INTERVAL,
        log_backup_count=settings.LOG_BACKUPS,
        log_format=settings.LOG_FORMAT,
        log_filters=settings.LOG_FILTERS
):
    """Init loggsetting."""
    logger = logging.getLogger()
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    if logger.filters:
        for log_filter in logger.filters:
            logger.removeFilter(log_filter)
    for log_filter in log_filters:
        logger.addFilter(logging.Filter(log_filter))
    if logdir:
        if not logfile:
            logfile = '%s.log' % os.path.basename(sys.argv[0])
        handler = logging.handlers.TimedRotatingFileHandler(
            os.path.join(logdir, logfile),
            when=log_interval_unit,
            interval=log_interval,
            backupCount=log_backup_count)
    else:
        if not logfile:
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = logging.handlers.TimedRotatingFileHandler(
                logfile,
                when=log_interval_unit,
                interval=log_interval,
                backupCount=log_backup_count)
    if loglevel in LOGLEVEL_MAPPING:
        logger.setLevel(LOGLEVEL_MAPPING[loglevel])

    formatter = logging.Formatter(
        log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
