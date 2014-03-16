from tornado.gen import coroutine

class UpdateConsumer():
  def __init__(self, queue):
    self._clients = set()

  def add(self, client):
    self._clients.add(client)
    self._runUpdateLoop

  def remove(self, client):
    self._clients.remove(client)

  @coroutine
  def _runUpdateLoop(self):
    while self._clients:
      message = queue.get()
      for client in self._clients:
        self.write_message(client, message)