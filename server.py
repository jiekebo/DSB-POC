#!/usr/bin/python

import multiprocessing
import signal
import sys
import pdb

from controller.TrainController import TrainController
from controller.StationController import StationController
from controller.SocketServer import SocketServer
from model.Station import Station
from model.Train import Train

queue = multiprocessing.Queue(1)
trainController = TrainController(queue)
socketServer = SocketServer(queue)

def signalHandler(sig, frame):
  trainController.shutdown()
  socketServer.shutdown()
  sys.exit(0)

if __name__ == '__main__':
  signal.signal(signal.SIGTERM, signalHandler)
  signal.signal(signal.SIGINT, signalHandler)

  trainController.start()
  socketServer.start()