#!/usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
import sys
from controller.TrackController import TrackController

from controller.TrainController import TrainController
from controller.SocketServer import SocketServer

trainQueue = multiprocessing.Queue(1)
trackQueue = multiprocessing.Queue(1)
trainController = TrainController(trainQueue)
trackController = TrackController(trainQueue, trackQueue)
socketServer = SocketServer(trackQueue)


def signalHandler(sig, frame):
    trainController.shutdown()
    socketServer.shutdown()
    sys.exit(0)

if __name__ == '__main__':
    #signal.signal(signal.SIGTERM, signalHandler)
    #signal.signal(signal.SIGINT, signalHandler)
    trainController.start()
    trackController.start()
    socketServer.start()