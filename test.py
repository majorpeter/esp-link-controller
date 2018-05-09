#!/usr/bin/env python3
import socket
from serial import rfc2217

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.3.123', 23))


def send_com_control(cmd):
    command = rfc2217.IAC + rfc2217.SB + rfc2217.COM_PORT_OPTION + rfc2217.SET_CONTROL +\
            cmd +\
            rfc2217.IAC + rfc2217.SE
    print(command)
    s.send(command)

s.send(rfc2217.IAC + rfc2217.WILL + rfc2217.COM_PORT_OPTION)
send_com_control(rfc2217.SET_CONTROL_DTR_OFF) ## GPIO0 -> hi
send_com_control(rfc2217.SET_CONTROL_DTR_ON)  ## GPIO0 -> low
send_com_control(rfc2217.SET_CONTROL_RTS_OFF) ## GPIO2 -> hi
send_com_control(rfc2217.SET_CONTROL_RTS_ON) ## GPIO2 -> low
