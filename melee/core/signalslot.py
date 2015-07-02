# -*- coding: utf-8 -*-
"""
use blinker to build a more easily using sync signal subscriber mechanism.

Using Example Code:
    >>>from melee.core.signalslot import signal, signalslot
    >>>sig1=signal('signal.test1')
    >>>sig2=signal('signal.test2')
    >>>sig3=signal('signal.test1')
    >>>sig1 == sig3
    True
    >>> @signalslot('signal.test1')
    ... def func1(v):
    ...     print 'in func1 %s' % v
    ...     return 'func1 result %s' % v
    ...
    >>> @signalslot('signal.test2')
    ... def func2(v):
    ...     print 'in func2 %s' % v
    ...     return 'func2 result %s' % v
    ...
    >>> @signalslot('signal.test1')
    ... def func3(v):
    ...     print 'in func3 %s' % v
    ...     return 'func3 result %s' % v
    ...
    >>> sig1.send('send1')
    in func1 send1
    in func3 send1
    [(<function func1 at 0x10da2aaa0>, 'func1 result send1'), (<function func3 at 0x10da2ac08>, 'func3 result send1')]
"""

from blinker import signal

def signalslot(name):
    def wrapped(func):
        sig = signal(name)
        sig.connect(func)
        return func
    return wrapped


if __name__ == '__main__':
    sig1 = signal('test.s1')
    sig11 = signal('test.s1')
    print sig1 is sig11
    print sig1 == sig11

    sig2 = signal('test.s2')
    print sig1 is sig2
    
    @signalslot('test.s1')
    def func1(v):
        print 'in func1 %s' % v
        return 'func1 result %s' % v

    @signalslot('test.s2')
    @signalslot('test.s1')
    def func2(v):
        print 'in func2 %s' % v
        return 'func2 result %s' % v

    print '++++++++++++++'
    print sig1.send('abc')
    print '++++++++++++++'
    print sig2.send('def')
