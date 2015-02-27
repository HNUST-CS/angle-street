from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from route import main

http_server = HTTPServer(WSGIContainer(main.app))
http_server.listen(3000)
IOLoop.instance().start()
