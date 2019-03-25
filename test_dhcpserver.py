from dhcp.server import DhcpServer
from dhcp.packet import *

import logging
from typing import cast
import socket
from ipaddress import IPv4Address, IPv4Interface

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(name)s - %(message)s')

if __name__ == '__main__':
    server = DhcpServer(IPv4Interface('192.168.0.255/24'))

    packet1 = DhcpPacket.fromArgs(
        OpCode.REQUEST,
        8,
        34,
        IPv4Address(0),
        IPv4Address(0),
        IPv4Address(0),
        4,
        MessageType.DISCOVER)

    ret1 = cast(DhcpPacket, server.recv(packet1))
    leaseTime = cast(int, ret1.leaseTime)
    print()

    packet2 = DhcpPacket.fromArgs(
        OpCode.REQUEST,
        8,
        34,
        IPv4Address(0),
        ret1.yourIp,
        ret1.serverIp,
        4,
        MessageType.REQUEST,
        leaseTime - 1)

    ret2 = server.recv(packet2)
    print()

    packet3 = DhcpPacket.fromArgs(
        OpCode.REQUEST,
        8,
        34,
        IPv4Address(0),
        ret1.yourIp,
        ret1.serverIp,
        4,
        MessageType.ACK,
        leaseTime - 2)

    ret3 = server.recv(packet3)
    print()
    print()

    packet4 = DhcpPacket.fromArgs(
        OpCode.REQUEST,
        8,
        34,
        IPv4Address(0),
        ret1.yourIp,
        ret1.serverIp,
        4,
        MessageType.RELEASE,
        leaseTime - 4)

    ret4 = server.recv(packet4)
    print()
    print()

    packet5 = DhcpPacket.fromArgs(
        OpCode.REQUEST,
        8,
        34,
        IPv4Address(0),
        ret1.yourIp + 20,
        ret1.serverIp,
        4,
        MessageType.REQUEST,
        leaseTime - 2)

    ret5 = server.recv(packet5)
    print()

    packet6 = DhcpPacket.fromArgs(
        OpCode.REQUEST,
        8,
        34,
        IPv4Address(0),
        ret1.yourIp + 20,
        ret1.serverIp,
        4,
        MessageType.ACK,
        leaseTime)

    ret6 = server.recv(packet6)
