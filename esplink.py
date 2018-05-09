#!/usr/bin/env python3
import socket
from serial import rfc2217


class EspLink:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.connect((self.ip_address, 23))
        self.send_will_com_control()

    """
    The sender of this command is willing to send com port control option commands.
    (Must be sent to the ESP before sending actual commands)
    """
    def send_will_com_control(self):
        self.socket.send(rfc2217.IAC + rfc2217.WILL + rfc2217.COM_PORT_OPTION)

    def send_com_control_byte(self, cmd_byte):
        command = rfc2217.IAC + rfc2217.SB + rfc2217.COM_PORT_OPTION + rfc2217.SET_CONTROL + \
                  cmd_byte + \
                  rfc2217.IAC + rfc2217.SE
        self.socket.send(command)

    def set_dtr(self, on):
        if on:
            self.send_com_control_byte(rfc2217.SET_CONTROL_DTR_ON)
        else:
            self.send_com_control_byte(rfc2217.SET_CONTROL_DTR_OFF)

    def set_rts(self, on):
        if on:
            self.send_com_control_byte(rfc2217.SET_CONTROL_RTS_ON)
        else:
            self.send_com_control_byte(rfc2217.SET_CONTROL_RTS_OFF)
