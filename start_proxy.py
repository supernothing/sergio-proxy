#!/usr/bin/env python
from twisted.web import http
from twisted.internet import reactor
from sergio_proxy import transparent_proxy
from UserMITM import UserMITM

transparent_proxy.mitm = UserMITM()

f = http.HTTPFactory()
f.protocol = transparent_proxy.TransparentProxy
reactor.listenTCP(8081,f)
reactor.run()
