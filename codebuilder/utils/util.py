from abc import ABCMeta
from abc import abstractmethod
import argparse
import ConfigParser
import datetime
import dateutil
import dateutil.tz
import json
from six import with_metaclass
import uuid
import yaml


PARSER = argparse.ArgumentParser(description='')
PARSED_ARGS = None


def init_args(args):
    global PARSED_ARGS
    PARSER.add_argument('args', nargs=argparse.REMAINDER)
    PARSED_ARGS = PARSER.parse_args(args)
    return PARSED_ARGS.args


class ConfigAttr(with_metaclass(ABCMeta)):
    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def delay(self):
        pass


def parse(obj, recursive=True, force=False):
    if isinstance(obj, ConfigAttr):
        if force or not obj.delay():
            return parse(obj.get(), recursive=recursive, force=force)
        else:
            return obj
    if recursive:
        if isinstance(obj, dict):
            return {
                item_key: parse(item_value, recursive=recursive, force=force)
                for item_key, item_value in obj.items()
            }
        elif isinstance(obj, list):
            return [
                parse(item, recursive=recursive, force=force) for item in obj
            ]
        elif isinstance(obj, tuple):
            return tuple([
                parse(item, recursive=recursive, force=force) for item in obj
            ])
        elif isinstance(obj, set):
            return set([
                parse(item, recursive=recursive, force=force) for item in obj
            ])
    return obj


class Argument(ConfigAttr):
    def __init__(self, *args, **kwargs):
        self.action = PARSER.add_argument(*args, **kwargs)

    def get(self):
        if PARSED_ARGS is None:
            raise ValueError("arguments are not initialized")
        return parse(getattr(PARSED_ARGS, self.action.dest), force=True)

    def delay(self):
        return False


class Proxy(ConfigAttr):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self._delay = kwargs.pop('delay', False)
        self.kwargs = kwargs

    def get(self):
        return parse(self.func(*self.args, **self.kwargs), force=True)

    def delay(self):
        return self._delay


class LazyObj(ConfigAttr):
    CACHE = {}

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self._delay = kwargs.pop('delay', False)
        self.kwargs = kwargs

    def get(self):
        self_id = id(self)
        if self_id not in LazyObj.CACHE:
            LazyObj.CACHE[self_id] = parse(
                self.func(*self.args, **self.kwargs), force=True
            )
        return LazyObj.CACHE[self_id]

    def delay(self):
        return self._delay


def merge_dict(first, second, override=False, recursive=True):
    ret = {}
    if recursive:
        for key, value in first.iteritems():
            if key in second:
                ret[key] = merge(
                    value, second[key], override=override, recursive=True
                )
            else:
                ret[key] = value
        for key, value in second.iteritems():
            if key in first:
                pass
            else:
                ret[key] = value
    else:
        if override:
            ret.update(first)
            ret.update(second)
        else:
            ret.update(second)
            ret.update(first)
    return ret


def merge_list(first, second):
    return first + second


def merge(first, second, override=False, recursive=True):
    if isinstance(first, dict) and isinstance(second, dict):
        return merge_dict(
            first, second, override=override, recursive=recursive
        )
    elif isinstance(first, list) and isinstance(second, list):
        return merge_list(first, second)
    else:
        if override:
            return second
        else:
            return first


def merge_all(configs):
    return reduce(merge, configs, {})


def load_configs(filenames):
    configs = []
    for filename in filenames:
        if any([filename.endswith('.yaml'), filename.endswith('.yml')]):
            with open(filename, 'r') as filehandler:
                configs.append(yaml.load(filehandler))
        elif filename.endswith('.json'):
            with open(filename, 'r') as filehandler:
                configs.append(json.load(filehandler))
        elif any([
            filename.endswith('.cfg'), filename.endswith('.ini'),
            filename.endswith('conf')
        ]):
            with open(filename, 'r') as filehandler:
                config = ConfigParser.RawConfigParser()
                config.readfp(filehandler)
                defaults = config.defaults()
                for section in config.sections():
                    defaults[section] = {}
                    for key, value in config.items(section):
                        defaults[section][key] = value
                configs.append(config)
        elif filename.endswith('.py'):
            config = {}
            execfile(filename, config, config)
            configs.append(config)
        else:
            raise Exception('file %s unrecognized format' % filename)
    return merge_all(configs)


def generate_uuid():
    return uuid.uuid4().hex


def datetime_now(timezone=None):
    utc_now = datetime.datetime.utcnow().replace(
        tzinfo=dateutil.tz.tzutc()
    )
    if timezone is not None:
        return utc_now.astimezone(
            dateutil.tz.gettz(timezone)
        )
    else:
        return utc_now
