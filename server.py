#!/usr/bin/python

import tornado.ioloop
import tornado.web
import tornado.websocket
import multiprocessing
from tornado.options import define, options, parse_command_line

from model.Train import Train
from controller.TrainController import TrainController
from model.Station import Station
from controller.StationController import StationController


queue = multiprocessing.Queue(1)
trainController = TrainController(queue)
manager = multiprocessing.Manager()
clients = dict()

"""
Tornado setup
"""
define("port", default=8888, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")
        print queue.get()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("id")
        self.stream.set_nodelay(True)
        clients[self.id] = {"id": self.id, "object": self}
        self.write_message("Hello there mate " + self.id)

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        print "Client %s received a message : %s" % (self.id, message)
        
    def on_close(self):
        if self.id in clients:
            del clients[self.id]

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/ws', WebSocketHandler),
])


def messageClients (clients):
  while True:
    print clients
    message = queue.get()
    #for client in clients:
    #  print client
    #  client['object'].write_message("wow you're consuming!!!")


if __name__ == '__main__':
  trainController.run()
  messageClientsProcess = multiprocessing.Process(target=messageClients, args=(clients, ))
  messageClientsProcess.start()
  parse_command_line()
  app.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

