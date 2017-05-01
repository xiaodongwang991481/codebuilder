import logging

from codebuilder.utils import logsetting
from codebuilder.utils import settings
from codebuilder.utils import util


logger = logging.getLogger(__name__)


def main():
    util.init_args()
    settings.init_config()
    logsetting.init_logging()
    logger.debug('test')


if __name__ == '__main__':
    main()
