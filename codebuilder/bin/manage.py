import logging

from codebuilder.utils import util
from codebuilder.utils import settings
from codebuilder.utils import logsetting

logger = logging.getLogger(__name__)

def main():
    util.init_args()
    settings.init_config()
    logsetting.init_logging()
    logger.debug('test')


if __name__ == '__main__':
    main()
