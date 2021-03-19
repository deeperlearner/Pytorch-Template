import json
from pathlib import Path
from itertools import repeat
from collections import OrderedDict
from functools import reduce
from operator import getitem


def ensure_dir(dirname):
    dirname = Path(dirname)
    if not dirname.is_dir():
        dirname.mkdir(parents=True, exist_ok=False)


def read_json(fname):
    fname = Path(fname)
    with fname.open('rt') as handle:
        return json.load(handle, object_hook=OrderedDict)


def write_json(content, fname):
    fname = Path(fname)
    with fname.open('wt') as handle:
        json.dump(content, handle, indent=4, sort_keys=False)


def inf_loop(data_loader):
    ''' wrapper function for endless data loader. '''
    for loader in repeat(data_loader):
        yield from loader


def set_by_path(tree, keys, value):
    '''Set a value in a nested object in tree by sequence of keys.'''
    keys = keys.split(';')
    get_by_path(tree, keys[:-1])[keys[-1]] = value


def get_by_path(tree, keys):
    '''Access a nested object in tree by sequence of keys.'''
    return reduce(getitem, keys, tree)


def msg_box(msg):
    row = len(msg)
    h = ''.join(['+'] + ['-' * row] + ['+'])
    result = h + f"\n|{msg}|\n" + h
    return result
