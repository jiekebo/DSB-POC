import multiprocessing

from tornado.options import define, options, parse_command_line
from tornado import websocket, web, ioloop, autoreload
from tornado.ioloop import PeriodicCallback

define("port", default=8888, help="run on the given port", type=int)


class WebSocketHandler(websocket.WebSocketHandler):
    def initialize(self, queue):
        self.clients = dict()
        self.queue = queue
        self.callback = PeriodicCallback(self.message_clients, 120)
        self.callback.start()

    def open(self, *args):
        self.id = self.get_argument("id")
        self.stream.set_nodelay(True)
        self.clients[self.id] = {"id": self.id, "object": self}

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        print "Client %s received a message : %s" % (self.id, message)

    def on_close(self):
        if self.id in self.clients:
            del self.clients[self.id]
            print "Removed client " + self.id

    def message_clients(self):
        message = self.queue.get()
        for client in self.clients:
            try:
                self.write_message(message)
            except:
                print "Message could not be written"


class SocketServer(multiprocessing.Process, websocket.WebSocketHandler):
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.app = web.Application([
            (r'/ws', WebSocketHandler, dict(queue=queue))
        ])

    def run(self):
        parse_command_line()
        self.app.listen(options.port)
        loop = ioloop.IOLoop.instance()
        autoreload.start(loop)
        loop.start()

    def shutdown(self):
        ioloop.IOLoop.instance().stop()