
# -*- coding: utf-8 -*-
import pytest

from easyirc import util
from easyirc.socket import Socket

import settings

from mocksocket import *

@pytest.mark.parametrize(['line', 'items'], [
    [':localhost PING :thepingstring', ['PING', 'thepingstring']],
    ['PRIVMSG #chan nick :this is the msg', ['PRIVMSG', '#chan', 'nick', 'this is the msg']],
])
def test_split(line, items):
    splited = util.cmdsplit(line)
    assert splited == items

socktypes = [[MockSocket]]
if settings.TEST_REALSERVER:
    socktypes.append([Socket])

@pytest.mark.parametrize(['SocketType'], [
    [Socket],
    [MockSocket],
])
def test_create(SocketType):
    connop = settings.CONNECTIONS[0]
    sock = SocketType((connop['host'], connop['port']), 'utf-8')
    msg = sock.dispatch()
    assert msg == 'CREATED'
    assert sock.dispatch() is None
    return sock

@pytest.mark.parametrize(['SocketType'], socktypes)
def test_enqueue(SocketType):
    print SocketType

    sock = test_create(SocketType)
    sock.connect()
    for msg in sock.dispatch_all():
        print msg
        assert msg == 'CONNECTED'
    assert sock.dispatch() is None

    def dispatch_useful():
        print '--> throwing out unusefuls'
        for msg in sock.dispatch_all():
            msg = util.cmdsplit(msg)
            print u' '.join(msg).encode('utf-8')
            if msg[0] == 'PING':
                sock.cmd('PONG', msg[1])
                continue
            if msg[0] == 'PRIVMSG':
                continue
            if msg[0] == '375':
                break
            if len(msg[0]) == 3 or msg[0] in ['NOTICE', 'MODE']:
                continue
            else:
                break
        else:
            print '<-- skipped all the trashes'
            return None
        print '<-- get a message'
        return msg

    sock.cmd('NICK', 'easybot')
    sock.cmdl('USER', 'easybot', 'localhost', '0', 'realname')

    msg = None
    while msg is None:
        sock.recv()
        msg = dispatch_useful()
    assert msg[0] == '375' # message of the day - for the registered user only

    connop = settings.CONNECTIONS[0]
    chan = connop['autojoins'][0]
    sock.cmd('JOIN', chan)
    msg = None
    while msg is None:
        sock.recv()
        msg = dispatch_useful()
    assert msg[0] == 'JOIN'
    sock.cmdl('PRIVMSG', chan, 'can you see my message?')
    sock.cmdl('PRIVMSG', chan, u'can you see my 한글 message?')
    sock.cmdl('PART', chan, u'test did end with non-ascii 한글')
    msg = None
    while msg is None:
        sock.recv()
        msg = dispatch_useful()
    assert msg[0] == 'PART'

if __name__ == '__main__':
    test_enqueue(Socket)
    test_enqueue(MockSocket)
