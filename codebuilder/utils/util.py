from abc import ABCMeta, abstractmethod
import argparse

PARSER = argparse.ArgumentParser(description='')
PARSED_ARGS = None


class ConfigAttr(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self):
        pass

def parse(obj):
    if isinstance(obj, ConfigAttr):
        value = obj.get()
    else:
        value = obj
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            value[item_key] = parse(item_value)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            value[i] = parse(item)
    elif isinstance(value, tuple):
        value_tuple = ()
        for item in value:
            value_tuple += (parse(item),)
    return value


class Argument(ConfigAttr):
    def __init__(self, *args, **kwargs):
        self.action = PARSER.add_argument(*args, **kwargs)

    def get(self):
        if PARSED_ARGS is None:
            raise ValueError("arguments are not initialized")
        return PARSED_ARGS.getattr(self.action.dest)


class Proxy(ConfigAttr):
    def __init__(self, func, cmd_arg, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def get(self):
        return self.func(*args, **kwargs)


class LazyObj(ConfigAttr):
    CACHE = {}

    def __init__(self, func, cmd_arg, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def get(self):
        self_id = id(self)
        if self_id not in LazyObj.CACHE:
            LazyObj.CACHE[self_id] = self.func(*args, **kwargs)
        return LazyObj.CACHE[self_id]
