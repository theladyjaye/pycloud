"""
Both AttributeDict and AliasDict were inspired by:
https://github.com/fabric/fabric/blob/master/fabric/utils.py
"""

class AttributeDict(dict):

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


class AliasDict(AttributeDict):

    aliases = None

    def __init__(self, arg=None):
        init = super(AliasDict, self).__init__

        if arg is not None:
            init(arg)
        else:
            init()

    def __getattr__(self, key):

        try:
            key = self.aliases[key]
        except KeyError:
            pass

        return super(AliasDict, self).__getattr__(key)

    def __setattr__(self, key, value):

        try:
            key = self.aliases[key]
        except KeyError:
            pass

        return super(AliasDict, self).__setattr__(key, value)
