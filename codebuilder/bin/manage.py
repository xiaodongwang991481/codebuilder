import logging
import os
import sys

from django.core.management import execute_from_command_line

from codebuilder.models import database
from codebuilder.utils import logsetting
from codebuilder.utils import settings
from codebuilder.utils import util


logger = logging.getLogger(__name__)


def main():
    args = util.init_args(sys.argv[1:])
    settings.init_config()
    logsetting.init_logging()
    database.init_database()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "codebuilder.utils.django_settings")
    execute_from_command_line(args)


if __name__ == '__main__':
    main()
