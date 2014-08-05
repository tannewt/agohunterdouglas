import threading
import time

import agoclient
import socket

CLIENT = agoclient.AgoConnection("hunterdouglas")
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HD_GATEWAY_ADDR = (agoclient.get_config_option("hunterdouglas", "server", ""),
                   agoclient.get_config_option("hunterdouglas", "port", "522"))
TIMEOUT = 10

def verify_socket():
  global SOCKET
  try:
    SOCKET.sendall("$dmy")
    print repr(recv_until("ack\n\r"))
  except socket.error as e:
    SOCKET.close()
    print "recreating socket"
    SOCKET = socket.create_connection(HD_GATEWAY_ADDR)
    SOCKET.settimeout(TIMEOUT)

def set_shade(internal_id, hd_value):
  verify_socket()
  SOCKET.sendall("$pss%s-04-%03d" % (internal_id, hd_value))
  recv_until("done")
  SOCKET.sendall("$rls")
  recv_until("act00-00-")
  return True

def recv_until(sentinal):
  info = ""
  while True:
    try:
      chunk = SOCKET.recv(1)
    except socket.timeout:
      break
    info += chunk
    if info.endswith(sentinal): break
    if not chunk: break
  return info

def message_handler(internal_id, content):
  print(internal_id, content)
  if content["command"] == "off":
    if set_shade(internal_id, 0):
      CLIENT.emit_event(internal_id, "event.device.statechanged", 0, "")
      print "updated"
  elif content["command"] == "on":
    if set_shade(internal_id, 255):
      CLIENT.emit_event(internal_id, "event.device.statechanged", 16, "")
      print "updated on"

print(dir(CLIENT))
CLIENT.add_handler(message_handler)

SOCKET.connect(HD_GATEWAY_ADDR)
SOCKET.settimeout(TIMEOUT) #in seconds
SOCKET.sendall("$dat")

info = recv_until("upd01-")

prefix = None
for line in info.split("\n"):
  line = line.strip()
  if not prefix:
    prefix = line[:2]
  elif not line.startswith(prefix):
    continue
  else:
    line = line[2:]
  if line.startswith("$cs"):
    pass
    # name of a shade
    print line
  elif line.startswith("$cp"):
    #id of a shade
    shade_id = line[3:5]
    state = line[-4:-1]
    state = str(int((int(state) / 255.) * 16))
    print "adding shade:", shade_id, state
    CLIENT.add_device(shade_id, "drapes")
    CLIENT.emit_event(shade_id, "event.device.statechanged", state, "")
  else:
    pass

CLIENT.run() #blocks

