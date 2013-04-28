
from .. import util

class CommandManager(object):
    def __init__(self, client, commands={}):
        self.client = client
        self.commands = commands

    def putln(self, command):
        items = util.split(command)
        self.put(items)

    def put(self, items):
        if not isinstance(items, util.Line):
            items = util.Line(items)
        command = self.commands[items.cmd]
        command.run(self, *items[1:])

    @property
    def socket(self):
        return self.client.socket

    def cmd(self, *args):
        self.socket.cmd(*args)

    def cmdl(self, *args):
        self.socket.cmdl(*args)


class BaseCommand(object):
    def __init__(self, action):
        self.action = action

    def run(self, manager, *items):
        """Override run to change how action works."""
        return self.action(manager, *items)


