import argparse
import os
import sys

from alembic import command as alembic_command
from alembic import config as alembic_config
from alembic import environment
from alembic import script as alembic_script
from alembic import util as alembic_util
import six

from codebuilder.utils import logsetting
from codebuilder.utils import settings
from codebuilder.utils import util


HEAD_FILENAME = 'HEAD'
HEADS_FILENAME = 'HEADS'
MIGRATION_DIR = os.path.join(
    os.path.dirname(__file__), 'alembic_migrations'
)
codebuilder_alembic_ini = os.path.join(
    os.path.dirname(__file__), 'alembic.ini'
)
PARSER = argparse.ArgumentParser(description='')


def do_alembic_command(config, cmd, revision=None, desc=None, **kwargs):
    args = []
    if revision:
        args.append(revision)

    if desc:
        alembic_util.msg(
            'Running %(cmd)s (%(desc)s)...' % {'cmd': cmd, 'desc': desc}
        )
    else:
        alembic_util.msg(
            'Running %(cmd)s ...' % {'cmd': cmd}
        )
    try:
        getattr(alembic_command, cmd)(config, *args, **kwargs)
    except alembic_util.CommandError as e:
        alembic_util.err(six.text_type(e))
    alembic_util.msg('OK')


def do_generic_show(config, cmd, namespace):
    kwargs = {'verbose': namespace.verbose}
    do_alembic_command(config, cmd, **kwargs)


def do_check_migration(config, cmd, namespace):
    do_alembic_command(config, 'heads')
    validate_head_files(config)


def do_upgrade(config, cmd, namespace):
    if not namespace.revision and not namespace.delta:
        raise SystemExit(_('You must provide a revision or relative delta'))
    else:
        revision = namespace.revision or ''
        if '-' in revision:
            raise SystemExit(_('Negative relative revision (downgrade) not '
                               'supported'))
        delta = namespace.delta
        if delta:
            if '+' in revision:
                raise SystemExit(_('Use either --delta or relative revision, '
                                   'not both'))
            if delta < 0:
                raise SystemExit(_('Negative delta (downgrade) not supported'))
            revision = '%s+%d' % (revision, delta)

        if revision == 'head':
            revision = 'heads'
        if not namespace.sql:
            run_sanity_checks(config, revision)
        do_alembic_command(
            config, cmd, revision=revision,
            sql=namespace.sql
        )


def no_downgrade(config, cmd, namespace):
    raise SystemExit(_("Downgrade no longer supported"))


def do_stamp(config, cmd, namespace):
    do_alembic_command(config, cmd,
                       revision=namespace.revision,
                       sql=namespace.sql)


def do_revision(config, cmd, namespace):
    kwargs = {
        'message': namespace.message,
        'autogenerate': namespace.autogenerate,
        'sql': namespace.sql,
    }
    do_alembic_command(config, cmd, **kwargs)
    update_head_files(config)


def _check_head(head_file, head):
    try:
        with open(head_file) as file_:
            observed_head = file_.read().strip()
    except IOError:
        pass
    else:
        if observed_head != head:
            alembic_util.err(
                'HEAD file does not match migration timeline '
                'head, expected: %(head)s' % {'head': head}
            )


def validate_head_files(config):
    '''Check that HEAD files contain the latest head for the branch.'''
    head_file = _get_head_file_path(config)
    heads_file = _get_heads_file_path(config)
    if not os.path.exists(head_file) and not os.path.exists(heads_file):
        alembic_util.err(_("Repository does not contain HEAD files"))
        return
    heads = _get_heads(config)
    for file_ in (head_file, heads_file):
        if os.path.exists(file_):
            if not heads:
                alembic_util.err(
                    'HEAD file contains no head'
                )
            if len(heads) > 1:
                alembic_util.err(
                    'HEAD file contains more than one head: %(heads)s' % {
                        'heads': heads
                    }
                )
            for head in heads:
                _check_head(file_, head)


def _get_heads(config):
    script = alembic_script.ScriptDirectory.from_config(config)
    return script.get_heads()


def update_head_files(config):
    '''Update HEAD files with the latest branch heads.'''
    heads = _get_heads(config)
    old_head_file = _get_head_file_path(config)
    old_heads_file = _get_heads_file_path(config)
    for file_ in (old_head_file, old_heads_file):
        with open(file_, 'w+') as f:
            for head in heads:
                f.write(head + '\n')


def _get_root_versions_dir(config):
    '''Return root directory that contains all migration rules.'''
    return os.path.join(MIGRATION_DIR, 'versions')


def _get_head_file_path(config):
    '''Return the path of the file that contains single head.'''
    return os.path.join(
        _get_root_versions_dir(config),
        HEAD_FILENAME)


def _get_heads_file_path(config):
    return os.path.join(
        _get_root_versions_dir(config),
        HEADS_FILENAME)


def _set_version_locations(config):
    '''Make alembic see all revisions in all migration branches.'''
    version_paths = [_get_root_versions_dir(config)]
    config.set_main_option('version_locations', ' '.join(version_paths))


def get_alembic_config():
    config = alembic_config.Config(codebuilder_alembic_ini)
    config.set_main_option(
        'script_location',
        MIGRATION_DIR
    )
    config.set_main_option('sqlalchemy.url', settings.DATABASE_URI)
    _set_version_locations(config)
    return config


def run_sanity_checks(config, revision):
    script_dir = alembic_script.ScriptDirectory.from_config(config)

    def check_sanity(rev, context):
        # TODO(ihrachyshka): here we use internal API for alembic; we may need
        # alembic to expose implicit_base= argument into public
        # iterate_revisions() call
        for script in script_dir.revision_map.iterate_revisions(
                revision, rev, implicit_base=True):
            if hasattr(script.module, 'check_sanity'):
                script.module.check_sanity(context.connection)
        return []

    with environment.EnvironmentContext(config, script_dir,
                                        fn=check_sanity,
                                        starting_rev=None,
                                        destination_rev=revision):
        script_dir.run_env()


def init_alembic_parsers(parser, args):
    subparsers = parser.add_subparsers(dest='subparser_name')
    for name in ['current', 'history', 'heads']:
        subparser = subparsers.add_parser(name)
        subparser.add_argument(
            '--verbose',
            action='store_true',
            help='Display more verbose output for the specified command'
        )
        subparser.set_defaults(func=do_generic_show)
    subparser = subparsers.add_parser('check_migration')
    subparser.set_defaults(func=do_check_migration)
    subparser = subparsers.add_parser('upgrade')
    subparser.add_argument('--delta', type=int)
    subparser.add_argument('--sql', action='store_true')
    subparser.add_argument('revision', nargs='?')
    subparser.add_argument(
        '--mysql-engine',
        default='',
        help='Change MySQL storage engine of current existing tables'
    )
    subparser.set_defaults(func=do_upgrade)
    subparser = subparsers.add_parser(
        'downgrade', help="(No longer supported)"
    )
    subparser.add_argument(
        'None', nargs='?', help="Downgrade not supported"
    )
    subparser.set_defaults(func=no_downgrade)
    subparser = subparsers.add_parser('stamp')
    subparser.add_argument('--sql', action='store_true')
    subparser.add_argument('revision')
    subparser.set_defaults(func=do_stamp)
    subparser = subparsers.add_parser('revision')
    subparser.add_argument('-m', '--message')
    subparser.add_argument('--sql', action='store_true')
    subparser.add_argument('--autogenerate', action='store_true')
    subparser.set_defaults(func=do_revision)


def parse_alembic_args(namespace, config):
    return namespace.func(config, namespace.subparser_name, namespace)


def main():
    util.init_args(
        sys.argv[1:], [init_alembic_parsers]
    )
    settings.init_config()
    logsetting.init_logging()
    config = get_alembic_config()
    return parse_alembic_args(util.PARSED_ARGS, config)
