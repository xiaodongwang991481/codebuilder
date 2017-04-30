import logging

from codebuilder.utils import settings
from codebuilder.utils import logsetting

logger = logging.getLogger(__name__)

def main():
    logsetting.init()
    logger.debug('test')


if __name__ == '__main__':
    main()
