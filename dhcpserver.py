from dhcp.server import DhcpServer
from dhcp.packet import DhcpPacket

import logging
import socket
from ipaddress import IPv4Address, IPv4Interface

SERVER_PORT = 4200
SERVER_INTERFACE = IPv4Interface('192.168.1.255/24')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(name)s - %(message)s')

log = logging.getLogger(__name__)


def parsePacket(packet: bytes) -> DhcpPacket:
    partialPacket = DhcpPacket.fromPacket(
        packet[:DhcpPacket.initialPacketSize])
    offset: int = DhcpPacket.initialPacketSize
    while partialPacket.bytesNeeded > 0:
        nextOffset = offset + partialPacket.bytesNeeded
        partialPacket.parseMore(
            packet[offset:offset + partialPacket.bytesNeeded])
        offset = nextOffset

    return partialPacket.packet


if __name__ == '__main__':
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('', SERVER_PORT))
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    log.info(f'Server bound to port {SERVER_PORT}')
    server = DhcpServer(SERVER_INTERFACE)

    while True:
        packetBytes = serverSocket.recv(4096)
        packet = parsePacket(packetBytes)
        response = server.recv(packet)
        if response is not None:
            serverSocket.sendto(
                response.encode(), (int(IPv4Address('255.255.255.255'), SERVER_PORT)))
