
from .. import util

class CommandManager(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs) # useful? useless?

        self['run'] = self # trick!

    def runln(self, client, command):
        items = util.cmdsplit(command)
        self.run(client, *items)

    def run(self, client, *items):
        items = util.CommandLine(items)
        command = self[items.cmd]
        command.run(client, *items[1:])

    def merge(self, manager, override=False):
        for cmd, action in manager.iteritems():
            if not override and cmd in self:
                continue
            self[cmd] = action

    def inherit(self, name, command, strict=True):
        """Works like 'push', but parent is accessible."""
        if name not in self:
            if strict:
                raise KeyError(name)
            parent = None
        else:
            parent = self[name]
        command.super = parent
        self[name] = command

    def disinherit(self, name, strict=True):
        """Works like 'pop'."""
        parent = self[name].super
        if parent:
            self[name] = parent
        else:
            if strict:
                raise KeyError(name)
            else:
                del(self[name])

    # decorators
    def command(self, command):
        if isinstance(command, BaseCommand):
            self.inherit(command.__name__, command, strict=False)
        elif callable(command):
            name = command.__name__
            command = SoleFunctionCommand(command)
            self[name] = command
        else:
            raise TypeError
        return command

    def override(self, command):
        if isinstance(command, BaseCommand):
            self.inherit(command.__name__, command, strict=True)
        elif callable(command):
            name = command.__name__
            command = FunctionCommand(command)
            self.inherit(name, command)
        else:
            raise TypeError
        return command


class BaseCommand(object):
    def __init__(self, super=None, category=None):
        self.super = super
        self.category = category

    def run(self, manager, *items):
        """Implement to define a command."""
        raise NotImplementedError


class FunctionCommand(BaseCommand):
    def __init__(self, action, super=None, category=None):
        BaseCommand.__init__(self, super, category)
        self.action = action

    def run(self, manager, *items):
        return self.action(manager, self.super, *items)


class SoleFunctionCommand(FunctionCommand):
    def run(self, manager, *items):
        return self.action(manager, *items)

