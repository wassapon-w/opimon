import socket
import select
import threading
import struct

import datetime

import logging
from binascii import hexlify, unhexlify

from ryu.ofproto import ofproto_common
from ryu.ofproto import ofproto_parser
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_protocol

from ryu.ofproto import ofproto_v1_0_parser
from ofproto import ofproto_v1_0_parser_extention

from ryu.lib import addrconv

from pymongo import MongoClient

# import log

LOG = logging.getLogger('Packet Monitor')

class MessageWatcherAgentThread(threading.Thread):
	def __init__(self, switch_socket, controller_host, controller_port):
		super(MessageWatcherAgentThread, self).__init__()

		self.controller_socket = socket.socket()
		self.controller_socket.connect((controller_host, controller_port))
		self.controller_socket.setblocking(0)
		self.controller_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.switch_socket = switch_socket
		self.switch_socket.setblocking(0)
		self.switch_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.is_alive = True
		self.datapath = ofproto_protocol.ProtocolDesc(version=0x01)
		self.id = None

		# Connect to database
		# client = MongoClient('localhost', 27017)
		# self.db = client['netspec']

	def run(self):
		while(self.is_alive):
			self._loop()

	def _drop_collections(self):
		self.db.flow_mods.drop()

	def _loop(self):
		# Initialization
		downstream_buf = bytearray()
		upstream_buf = bytearray()
		socks = [self.controller_socket, self.switch_socket]

		# Wait for receive
		rsocks, wsocks, esocks = select.select(socks, [], [])

		for sock in rsocks:

			# Receive packet
			ret = sock.recv(2048)

			if not ret:
				self._close()
				break

			if sock is self.controller_socket:
				downstream_buf += ret
				self._parse(downstream_buf, self._downstream_parse)

			if sock is self.switch_socket:
				upstream_buf += ret
				self._parse(upstream_buf, self._upstream_parse)

	def _close(self):
		self.controller_socket.close()
		self.switch_socket.close()
		self.is_alive = False

	def _parse(self, buf, parse):
		required_len = ofproto_common.OFP_HEADER_SIZE
		while len(buf) >= required_len:
			(version,
			 msg_type,
			 msg_len,
			 xid) = ofproto_parser.header(buf)
			if len(buf) < msg_len:
				break
			pkt = buf[:msg_len]
			parse(pkt)
			buf = buf[msg_len:]

	# Controller to Switch
	def _downstream_parse(self, pkt):
		(version, msg_type, msg_len, xid) = ofproto_parser.header(pkt)

		# Controller command messages
		if msg_type == ofproto_v1_0.OFPT_FLOW_MOD:
			LOG.info('Forward FLOW_MOD Message at DOWNSTREAM')

			msg = ofproto_v1_0_parser_extention.OFPFlowMod.parser(
				self.datapath, version, msg_type, msg_len, xid, pkt)

			# Write to database
			# db_message = {"switch": self.id,
			# 			  "message": {
			# 				  "header": {
			# 					  "version": version,
			# 					  "type": msg_type,
			# 					  "length": msg_len,
			# 					  "xid": xid
			# 				  },
			# 				  "match": {
			# 					  "wildcards": msg.match.wildcards,
			# 					  "in_port": msg.match.in_port,
			# 					  #"dl_src": hexlify(msg.match.dl_src.encode()),
			# 					  #"dl_dst": hexlify(msg.match.dl_dst.encode()),
			# 					  "dl_src": hexlify(msg.match.dl_src),
			# 					  "dl_dst": hexlify(msg.match.dl_dst),
			# 					  "dl_vlan": msg.match.dl_vlan,
			# 					  "dl_vlan_pcp": msg.match.dl_vlan_pcp,
			# 					  "dl_type": msg.match.dl_type,
			# 					  "nw_tos": msg.match.nw_tos,
			# 					  "nw_proto": msg.match.nw_proto,
			# 					  "nw_src": msg.match.nw_src,
			# 					  "nw_dst": msg.match.nw_dst,
			# 					  "tp_src": msg.match.tp_src,
			# 					  "tp_dst": msg.match.tp_dst
			# 				  },
			# 				  "cookie": msg.cookie,
			# 				  "command": msg.command,
			# 				  "idle_timeout": msg.idle_timeout,
			# 				  "priority": msg.priority,
			# 				  "buffer_id": msg.buffer_id,
			# 				  "out_port": msg.out_port,
			# 				  "flags": msg.flags,
			# 				  "actions": []
			# 			  },
			# 			  "timestamp": datetime.datetime.utcnow()}

			# for action in msg.actions:
			# 	if action.type == ofproto_v1_0.OFPAT_OUTPUT:
			# 		db_message["message"]["actions"].append({"type": action.type,
			# 										   "len": action.len,
			# 										   "port": action.port,
			# 										   "max_len": action.max_len})

			# Insert to database
			# self.db.flow_mods.insert_one(db_message)

			#t = threading.Thread(target=self.db.flow_mods.insert_one, args=(db_message,))
			#t.start()
		self.switch_socket.send(pkt)

	# Switch to Controller
	def _upstream_parse(self, pkt):
		(version, msg_type, msg_len, xid) = ofproto_parser.header(pkt)

		# Switch configuration messages
		if msg_type == ofproto_v1_0.OFPT_FEATURES_REPLY:
			LOG.info('Forward FEATURES_REPLY Message at UPSTREAM')

			msg = ofproto_v1_0_parser.OFPSwitchFeatures.parser(
				self.datapath, version, msg_type, msg_len, xid, pkt)

			self.id = msg.datapath_id
			self.ports= msg.ports

		# Asynchronous messages
		#elif msg_type == ofproto_v1_0.OFPT_FLOW_REMOVED:
		#    LOG.info('Forward FLOW_REMOVED Message at UPSTREAM')

		#    msg = ofproto_v1_0_parser.OFPFlowRemoved.parser(
		#        self.datapath, version, msg_type, msg_len, xid, pkt)

		#    db_message = {"switch": self.id,
		#                  "message.match": {
		#                      "wildcards": msg.match.wildcards,
		#                      "in_port": msg.match.in_port,
		#                      "dl_src": hexlify(msg.match.dl_src.encode()),
		#                      "dl_dst": hexlify(msg.match.dl_dst.encode()),
		#                      "dl_vlan": msg.match.dl_vlan,
		#                      "dl_type": msg.match.dl_type,
		#                      "nw_tos": msg.match.nw_tos,
		#                      "nw_proto": msg.match.nw_proto,
		#                      "nw_src": msg.match.nw_src,
		#                      "nw_dst": msg.match.nw_dst,
		#                      "tp_src": msg.match.tp_src,
		#                      "tp_dst": msg.match.tp_dst}
		#                      }
 
		#    self.db.flow_mods.remove(db_message)

		#elif msg_type == ofproto_v1_0.OFPT_PACKET_IN:
		#    LOG.info('Forward PACKET_IN Message at UPSTREAM')

		#    msg = ofproto_v1_0_parser.OFPPacketIn.parser(
		#        self.datapath, version, msg_type, msg_len, xid, pkt)

		#    db_message = {"switch": self.id,
		#                  "message": {
		#                      "header": {
		#                          "version": version,
		#                          "type": msg_type,
		#                          "length": msg_len,
		#                          "xid": xid
		#                      },
		#                      "buffer_id": msg.buffer_id,
		#                      "total_len": msg.total_len,
		#                      "in_port": msg.in_port,
		#                      "reason": msg.reason,
		#                      "data": hexlify(msg.data)}
		#                  }

		#    self.db.packet_in.insert_one(db_message)

		self.controller_socket.send(pkt)


class MessageWatcher(object):

	def __init__(self, listen_host, listen_port, forward_host, forward_port):
		super(MessageWatcher, self).__init__()
		# Create socket for downstream connection
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((listen_host, listen_port))
		sock.listen(5)
		self.listen_socket = sock

		# Upstream host switch settings
		self.forward_host = forward_host
		self.forward_port = forward_port
		self.threads = []

	def _handle(self, sock):
		thread = MessageWatcherAgentThread(sock, self.forward_host, self.forward_port)
		thread.start()
		self.threads.append(thread)

	def start(self):
		# self.logger.info("Running")
		self.run()

	def run(self):
		while(True):
			self._loop()

	def _loop(self):
		conn, addr = self.listen_socket.accept()
		self._handle(conn)

if __name__ == '__main__':

	# log.init_log()

	LISTEN_HOST, LISTEN_PORT = '0.0.0.0', 6643
	FORWARD_HOST, FORWARD_PORT = 'localhost', 6653
	manager = MessageWatcher(LISTEN_HOST, LISTEN_PORT, FORWARD_HOST, FORWARD_PORT)
	manager.start()
