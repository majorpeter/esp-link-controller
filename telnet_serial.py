#!/usr/bin/env python3
import socket
from sys import argv

import serial
from serial import rfc2217


def DEBUG(message):
    pass


class TelnetSerial:
    def __init__(self, ip_address, port=23, baud_rate=None, parity=None):
        self.ip_address = ip_address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.connect((self.ip_address, self.port))
        if not self.send_will_com_control():
            raise BaseException('Cannot control COM port')
        if baud_rate is not None:
            self.send_baud_rate(baud_rate)
        if parity is not None:
            self.send_parity(parity)

    """
    The sender of this command is willing to send com port control option commands.
    (Must be sent to the ESP before sending actual commands)
    """
    def send_will_com_control(self):
        self.socket.send(rfc2217.IAC + rfc2217.WILL + rfc2217.COM_PORT_OPTION)
        response = self.socket.recv(3)
        if response[0] == rfc2217.IAC[0] and response[1] == rfc2217.DO[0] and response[2] == rfc2217.COM_PORT_OPTION[0]:
            return True
        if response[0] == rfc2217.IAC[0] and response[1] == rfc2217.DONT[0] and response[2] == rfc2217.COM_PORT_OPTION[0]:
            return False
        raise BaseException('Cannot process response: ' + str(response))

    def send_baud_rate(self, baud_rate):
        """
        set baud rate on remote end
        :param baud_rate: baud rate in Hz
        """
        baud_bytes = bytes([
            (baud_rate & 0xff000000) >> 24,
            (baud_rate & 0x00ff0000) >> 16,
            (baud_rate & 0x0000ff00) >> 8,
            baud_rate & 0x000000ff
        ])
        self.socket.send(rfc2217.IAC + rfc2217.SB + rfc2217.COM_PORT_OPTION + rfc2217.SET_BAUDRATE + baud_bytes +
                         rfc2217.IAC + rfc2217.SE)

    def send_parity(self, parity=serial.PARITY_NONE):
        """
        set parity on remote end
        :param parity: parity setting from serial module
        :return:
        """
        if parity not in rfc2217.RFC2217_PARITY_MAP:
            raise BaseException('Invalid parity setting (%s)!' % parity)
        parity_byte = bytes([rfc2217.RFC2217_PARITY_MAP[parity]])
        self.socket.send(rfc2217.IAC + rfc2217.SB + rfc2217.COM_PORT_OPTION + rfc2217.SET_PARITY + parity_byte +
                         rfc2217.IAC + rfc2217.SE)

    def send_com_control_byte(self, cmd_byte):
        command = rfc2217.IAC + rfc2217.SB + rfc2217.COM_PORT_OPTION + rfc2217.SET_CONTROL + \
                  cmd_byte + \
                  rfc2217.IAC + rfc2217.SE
        self.socket.send(command)

    def setDTR(self, level):
        DEBUG('DTR ' + str(level))
        if level:
            self.send_com_control_byte(rfc2217.SET_CONTROL_DTR_ON)
        else:
            self.send_com_control_byte(rfc2217.SET_CONTROL_DTR_OFF)

    def setRTS(self, level):
        DEBUG('RTS ' + str(level))
        if level:
            self.send_com_control_byte(rfc2217.SET_CONTROL_RTS_ON)
        else:
            self.send_com_control_byte(rfc2217.SET_CONTROL_RTS_OFF)

    def write(self, data):
        telnet_escaped_data = bytearray()
        for byte in data:
            telnet_escaped_data.append(byte)
            if byte == 0xff:
                telnet_escaped_data.append(byte)
        DEBUG('Write escaped: %s (was %s)' % (str(telnet_escaped_data), str(data)))
        self.socket.send(telnet_escaped_data)

    def read(self, size=1):
        data = self.socket.recv(size)
        DEBUG('Received: ' + str(data))
        return data


def main():
    ip_address = argv[1]
    flag = argv[2]
    value = argv[3]

    if value in ['on', '1']:
        value = True
    elif value in ['off', '0']:
        value = False
    else:
        raise BaseException('Unsupported value %s (use on|1|off|0)' % value)

    if flag == 'dtr':
        TelnetSerial(ip_address).setDTR(value)
    elif flag == 'rts':
        TelnetSerial(ip_address).setRTS(value)
    else:
        raise BaseException('Unsupported flag %s (use dtr|rts' % flag)


if __name__ == "__main__":
    main()
