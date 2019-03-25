from dhcp.packet import DhcpPacket, MessageType, OpCode
from dhcp.transaction import Transaction, TransactionType

import logging
from typing import Optional, Tuple, Generator
from ipaddress import IPv4Address

log = logging.getLogger(__name__)


class ServerTransaction(Transaction):
    """Class for representing an ongoing session with a client.

    An ongoing session means there
    is more than 1 packet exchanged.
    A DHCP release is not a session.

    Various differing pieces of data
    are required for various transaction types.
    It is the responsibility of the server
    to set the appropriate variables
    for the appropriate session type.

    This class forms a tagged union or sum type
    with the self.transactionType being the tag.
    """

    __transaction: Optional[
        Generator[DhcpPacket, DhcpPacket, Optional[DhcpPacket]]]

    yourIp: IPv4Address
    serverIp: IPv4Address
    leaseTime: int  # unsigned

    def __init__(self):
        self.__transaction = None

    def __gen(self, packet: DhcpPacket) -> Generator[
            DhcpPacket, DhcpPacket, Optional[DhcpPacket]]:
        """Implements self.recv as a coroutine using a python generator."""

        self.transactionId = packet.transactionId
        self.clientHardwareAddr = packet.clientHardwareAddr

        if packet.messageType is MessageType.DISCOVER:
            self.transactionType = TransactionType.DISCOVER
            log.info('Start DISCOVER transaction')
            log.info(
                'DISCOVER transaction: Reply with OFFER of '
                f'{self.yourIp} for {self.leaseTime} seconds')
            packet = yield DhcpPacket.fromArgs(
                OpCode.REPLY,
                self.transactionId,
                packet.secondsElapsed,
                packet.clientIp,
                self.yourIp,
                self.serverIp,
                packet.clientHardwareAddr,
                MessageType.OFFER,
                self.leaseTime)

            if packet.messageType is MessageType.REQUEST:
                log.info(
                    'DISCOVER transaction: Recieved REQUEST of '
                    f'{packet.yourIp} for {packet.leaseTime} seconds')
                return DhcpPacket.fromArgs(
                    OpCode.REPLY,
                    self.transactionId,
                    packet.secondsElapsed,
                    packet.clientIp,
                    self.yourIp,
                    self.serverIp,
                    packet.clientHardwareAddr,
                    MessageType.ACK,
                    self.leaseTime)
            else:
                raise ValueError(
                    f'Expected DHCP REQUEST. Got {packet.messageType.name}.')

        elif packet.messageType is MessageType.REQUEST:
            self.transactionType = TransactionType.RENEW
            log.info('Start RENEW transaction')
            log.info(
                'RENEW transaction: Recieved REQUEST of '
                f'{packet.yourIp} for {packet.leaseTime} seconds')
            packet = yield DhcpPacket.fromArgs(
                OpCode.REPLY,
                self.transactionId,
                packet.secondsElapsed,
                packet.clientIp,
                self.yourIp,
                self.serverIp,
                packet.clientHardwareAddr,
                MessageType.ACK,
                self.leaseTime)

            if packet.messageType is MessageType.ACK:
                return None
            else:
                raise ValueError(
                    f'Expected DHCP ACK. Got {packet.messageType.name}.')

        else:
            raise ValueError('Unsupported transaction.')

    def recv(self, packet: DhcpPacket) -> Tuple[bool, Optional[DhcpPacket]]:
        """Receive a packet from the client.

        Returns a bool that is true
        when the transaction has finished
        and an optional DhcpPacket that
        is to be returned to the client if not None.
        """

        try:
            if self.__transaction is None:
                self.__transaction = self.__gen(packet)
                return False, next(self.__transaction)
            else:
                return False, self.__transaction.send(packet)
        except StopIteration as ex:
            return True, ex.value
