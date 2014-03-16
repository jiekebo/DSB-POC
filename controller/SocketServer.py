import multiprocessing

from tornado.options import define, options, parse_command_line
from tornado import websocket, web, ioloop
from tornado.gen import coroutine

define("port", default=8888, help="run on the given port", type=int)

class IndexHandler(web.RequestHandler):
  @web.asynchronous
  def get(self):
    self.render("../index.html")

class WebSocketHandler(websocket.WebSocketHandler):
  def initialize(self, queue):
    self.clients = dict()
    self.queue = queue

  def open(self, *args):
    self.id = self.get_argument("id")
    self.stream.set_nodelay(True)
    self.clients[self.id] = {"id": self.id, "object": self}

    self.write_message("Hello there mate " + self.id)
    WebSocketHandler.messageClients(self)

  def on_message(self, message):
    """
    when we receive some message we want some message handler..
    for this example i will just print message to console
    """
    print "Client %s received a message : %s" % (self.id, message)
        
  def on_close(self):
    if self.id in self.clients:
      del self.clients[self.id]

  @coroutine
  def messageClients(self):
    while self.clients:
      message = self.queue.get()
      for client in self.clients:
        try:
          #pdb.set_trace()
          self.write_message("hullo")
        except:
          print "Message could not be written"

class SocketServer(multiprocessing.Process, websocket.WebSocketHandler):
  def __init__(self, queue):
    multiprocessing.Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.app = web.Application([
      (r'/', IndexHandler),
      (r'/ws', WebSocketHandler, dict(queue=queue)),
    ])

  def run(self):
    parse_command_line()
    self.app.listen(options.port)
    ioloop.IOLoop.instance().start()

  def shutdown(self):
    print "Shutdown initiated"
    ioloop.IOLoop.instance().stop()