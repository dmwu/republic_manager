#!/usr/bin/python
import socket
import time

class sender(object):
  """docstring for ClassName"""
  def __init__(self, TCP_IP = "168.7.23.151", TCP_PORT = 40000, MESSAGE = "Hello, World!"):
    super(sender, self).__init__()
    self.MESSAGE = MESSAGE
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((TCP_IP, TCP_PORT))

  def send_one(self):
    self.sock.send(self.MESSAGE)

  def close(self):
    self.sock.close()


if __name__ == '__main__':
  s = sender();
  s.send_one()
  time.sleep(1)
  s.send_one()
  time.sleep(1)
  s.send_one()
  time.sleep(1)
  s.send_one()
  time.sleep(1)
  s.send_one()
  time.sleep(1)
  s.send_one()
  s.close()

