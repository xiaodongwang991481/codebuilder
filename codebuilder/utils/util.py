from abc import ABCMeta, abstractmethod
import argparse
import yaml
import json
import ConfigParser


PARSER = argparse.ArgumentParser(description='')
PARSED_ARGS = None


class ConfigAttr(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def delay(self):
        pass


def parse(obj, recursive=True, force=False):
    if isinstance(obj, ConfigAttr):
        if force or not obj.delay()
            value = obj.get()
        else:
            return obj
    else:
        value = obj
    if recursive:
        if isinstance(value, dict):
            return {item_key: parse(item_value, recursive=recursive, force=force) for item_key, item_value in value.items()}
        elif isinstance(value, list):
            return [parse(item, recursive=recursive, force=force) for item in value]
        elif isinstance(value, tuple):
            return tuple([parse(item, recursive=recursive, force=force) for item in value])
    return value


class Argument(ConfigAttr):
    def __init__(self, *args, **kwargs):
        self.action = PARSER.add_argument(*args, **kwargs)

    def get(self):
        if PARSED_ARGS is None:
            raise ValueError("arguments are not initialized")
        return PARSED_ARGS.getattr(self.action.dest)

    def delay(self):
        return False

class Proxy(ConfigAttr):
    def __init__(self, func, delay=False, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._delay = delay

    def get(self):
        return self.func(*args, **kwargs)

    def delay(self):
        return self._delay


class LazyObj(ConfigAttr):
    CACHE = {}

    def __init__(self, func, delay, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._delay = delay

    def get(self):
        self_id = id(self)
        if self_id not in LazyObj.CACHE:
            LazyObj.CACHE[self_id] = self.func(*args, **kwargs)
        return LazyObj.CACHE[self_id]

    def delay(self):
        return self._delay


def merge_dict(first, second, override=False, recursive=True):
    ret = {}
    if recursive:
        for key, value in first.iteritems():
            if key in second:
                ret[key] = merge(value, second[key], override=override, recursive=True)
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
        return merge_dict(first, second, override=override, recursive=recursive)
    elif isinstance(fist, list) and isinstance(second, list):
        return merge_list(first, second)
    else:
        if first is None:
            return second
        elif second is None:
            return first
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
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            with open(filename, 'r') as filehandler:
                configs.append(yaml.load(filehandler))
        elif filename.endswith('.json'):
            with open(filename, 'r') as filehandler:
                configs.append(json.load(filehandler))
        elif filename.endswith('.cfg') or filename.endswith('.ini') or filename.endswith('conf'):
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
