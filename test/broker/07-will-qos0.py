#!/usr/bin/env python

# Test whether a client will is transmitted correctly.

import subprocess
import socket
import time

import inspect, os, sys
# From http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import mosq_test

rc = 1
mid = 53
keepalive = 60
connect_packet = mosq_test.gen_connect("will-qos0-test", keepalive=keepalive)
connack_packet = mosq_test.gen_connack(rc=0)

subscribe_packet = mosq_test.gen_subscribe(mid, "will/qos0/test", 0)
suback_packet = mosq_test.gen_suback(mid, 0)

publish_packet = mosq_test.gen_publish("will/qos0/test", qos=0, payload="will-message")

broker = subprocess.Popen(['../../src/mosquitto', '-p', '1888'], stderr=subprocess.PIPE)

try:
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(("localhost", 1888))
    sock.send(connect_packet)

    if mosq_test.expect_packet(sock, "connack", connack_packet):
        sock.send(subscribe_packet)

        if mosq_test.expect_packet(sock, "suback", suback_packet):
            will = subprocess.Popen(['./07-will-qos0-helper.py'])
            will.wait()

            if mosq_test.expect_packet(sock, "publish", publish_packet):
                rc = 0

    sock.close()
finally:
    broker.terminate()
    broker.wait()
    if rc:
        (stdo, stde) = broker.communicate()
        print(stde)

exit(rc)

