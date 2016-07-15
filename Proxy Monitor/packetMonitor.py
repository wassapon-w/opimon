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
from ryu.ofproto.ether import ETH_TYPE_LLDP

from ryu.lib.packet import packet, ethernet, lldp
from ryu.lib.dpid import dpid_to_str, str_to_dpid
from ryu.ofproto import ofproto_v1_0_parser
from ofproto import ofproto_v1_0_parser_extention

from ryu.ofproto import ofproto_v1_0_parser
from ryu.lib import addrconv

from pymongo import MongoClient

# import log

LOG = logging.getLogger('OpenFlow Monitor')

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

		# Connect to database
		client = MongoClient('sd-lemon.naist.jp', 9999)
		self.db = client.test

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
		# print(pkt);

		# Controller command messages
		if msg_type == ofproto_v1_0.OFPT_FLOW_MOD:
			LOG.info('Forward FLOW_MOD Message at DOWNSTREAM')

			msg = ofproto_v1_0_parser_extention.OFPFlowMod.parser(
				self.datapath, version, msg_type, msg_len, xid, pkt)

			# print(msg);

			# Write to database
			db_message = {"switch": self.id,
						  "message": {
							  "header": {
								  "version": version,
								  "type": msg_type,
								  "length": msg_len,
								  "xid": xid
							  },
							  "match": {
								  "wildcards": msg.match.wildcards,
								  "in_port": msg.match.in_port,
								  "dl_src": hexlify(msg.match.dl_src),
								  "dl_dst": hexlify(msg.match.dl_dst),
								  "dl_vlan": msg.match.dl_vlan,
								  "dl_vlan_pcp": msg.match.dl_vlan_pcp,
								  "dl_type": msg.match.dl_type,
								  "nw_tos": msg.match.nw_tos,
								  "nw_proto": msg.match.nw_proto,
								  "nw_src": msg.match.nw_src,
								  "nw_dst": msg.match.nw_dst,
								  "tp_src": msg.match.tp_src,
								  "tp_dst": msg.match.tp_dst
							  },
							  "cookie": msg.cookie,
							  "command": msg.command,
							  "idle_timeout": msg.idle_timeout,
							  "hard_timeout": msg.hard_timeout,
							  "priority": msg.priority,
							  "buffer_id": msg.buffer_id,
							  "out_port": msg.out_port,
							  "flags": msg.flags,
							  "actions": []
						  },
						  "timestamp": datetime.datetime.utcnow()}

			for action in msg.actions:
				db_message["message"]["actions"].append(vars(action));

			# Insert to database
			self.db.flow_mods.insert_one(db_message)

			#t = threading.Thread(target=self.db.flow_mods.insert_one, args=(db_message,))
			#t.start()

		elif msg_type == ofproto_v1_0.OFPT_PACKET_OUT:
			self.db.packet_out.insert_one({"Switch": self.id, "Type": msg_type, "Timestamp": datetime.datetime.utcnow()})

		elif msg_type == ofproto_v1_0.OFPT_ECHO_REPLY:
			msg = ofproto_v1_0_parser.OFPEchoReply.parser(
				self.datapath, version, msg_type, msg_len, xid, pkt)

			print(msg)

			self.db.echo_reply.insert_one({"Switch": self.id, "Type": msg_type, "Timestamp": datetime.datetime.utcnow()})

		self.db.all_packet.insert_one({"Switch": self.id, "Type": msg_type, "Timestamp": datetime.datetime.utcnow()})
		self.switch_socket.send(pkt)

	# Switch to Controller
	def _upstream_parse(self, pkt):
		(version, msg_type, msg_len, xid) = ofproto_parser.header(pkt)

		# Switch configuration messages
		if msg_type == ofproto_v1_0.OFPT_FEATURES_REPLY:
			LOG.info('Forward FEATURES_REPLY Message at UPSTREAM')

			msg = ofproto_v1_0_parser.OFPSwitchFeatures.parser(self.datapath, version, msg_type, msg_len, xid, pkt)
			match = ofproto_v1_0_parser.OFPMatch(dl_type=ETH_TYPE_LLDP, dl_dst=lldp.LLDP_MAC_NEAREST_BRIDGE)
			cookie = 0
			command = ofproto_v1_0.OFPFC_ADD
			idle_timeout = hard_timeout = 0
			priority = 0
			buffer_id= ofproto_v1_0.OFP_NO_BUFFER
			out_port = ofproto_v1_0.OFPP_NONE
			flags = 0
			actions = [ofproto_v1_0_parser.OFPActionOutput(ofproto_v1_0.OFPP_CONTROLLER)]
			mod = ofproto_v1_0_parser.OFPFlowMod(self.datapath, match, cookie, command, idle_timeout, hard_timeout, priority, buffer_id, out_port, flags, actions)
			mod.serialize()

			# self.switch_socket.sendall(mod.buf)

			self.id = msg.datapath_id
			self.ports= msg.ports

			for port in self.ports.values():
				pkt_lldp = packet.Packet()

				dst = lldp.LLDP_MAC_NEAREST_BRIDGE
				src = port.hw_addr
				ethertype = ETH_TYPE_LLDP
				eth_pkt = ethernet.ethernet(dst, src, ethertype)
				pkt_lldp.add_protocol(eth_pkt)

				tlv_chassis_id = lldp.ChassisID(
					subtype=lldp.ChassisID.SUB_LOCALLY_ASSIGNED,
					chassis_id='dpid:%s' % dpid_to_str(self.id))

				tlv_port_id = lldp.PortID(subtype=lldp.PortID.SUB_PORT_COMPONENT,
										  port_id=struct.pack('!I', port.port_no))

				tlv_ttl = lldp.TTL(ttl=120)
				tlv_desc = lldp.PortDescription(port_description="ProxyTopologyMonitorLLDP")
				tlv_end = lldp.End()

				tlvs = (tlv_chassis_id, tlv_port_id, tlv_ttl, tlv_desc, tlv_end)
				lldp_pkt = lldp.lldp(tlvs)
				pkt_lldp.add_protocol(lldp_pkt)

				pkt_lldp.serialize()

				actions = [ofproto_v1_0_parser.OFPActionOutput(port.port_no)]
				out = ofproto_v1_0_parser.OFPPacketOut(
					datapath=self.datapath, in_port=ofproto_v1_0.OFPP_CONTROLLER,
					buffer_id=ofproto_v1_0.OFP_NO_BUFFER, actions=actions,
					data=pkt_lldp.data)
				out.serialize()

				t = threading.Timer(1, self.switch_socket.sendall, (out.buf,))
				t.start()
				LOG.info('Send LLDP Message to UPSTREAM')

		# Asynchronous messages
		elif msg_type == ofproto_v1_0.OFPT_PACKET_IN:
			LOG.info('Forward PACKET_IN Message at UPSTREAM')

			msg = ofproto_v1_0_parser.OFPPacketIn.parser(
				self.datapath, version, msg_type, msg_len, xid, pkt)
			pkt_msg = packet.Packet(msg.data)

			if pkt_msg.get_protocol(ethernet.ethernet).ethertype == ETH_TYPE_LLDP:
				LOG.info('Forward PACKET_IN LLDP Message at UPSTREAM')
				lldp_msg = pkt_msg.get_protocol(lldp.lldp)

				# if lldp_msg:
				if lldp_msg.tlvs[3].tlv_info == "ProxyTopologyMonitorLLDP":

					(port,) = struct.unpack('!I', lldp_msg.tlvs[1].port_id)
					switch_src = str_to_dpid(lldp_msg.tlvs[0].chassis_id[5:])

					# print("----------------------------")
					print(lldp_msg)

					# Write to database
					self.db.topology.insert_one({"switch_dst": self.id,
												 "port_dst": msg.in_port,
												 "switch_src": switch_src,
												 "port_src": port,
												 "timestamp": datetime.datetime.utcnow()})

					#dict = msg.to_jsondict().update(lldp_msg.to_jsondict())
					#self.db.topology_watcher.insert_one([msg.to_jsondict(), lldp_msg.to_jsondict()])

					return

				elif lldp_msg.tlvs[3].tlv_info != "ProxyTopologyMonitorLLDP":
					# print(lldp_msg)
					print("Controller LLDP packet")

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

		# elif msg_type == ofproto_v1_0.OFPT_PACKET_IN:
		# 	self.db.packet_in.insert_one({"Switch": self.id, "Type": msg_type, "Timestamp": datetime.datetime.utcnow()})
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

		# elif msg_type == ofproto_v1_0.OFPT_ECHO_REQUEST:
		# 	self.db.echo_request.insert_one({"Switch": self.id, "Type": msg_type, "Timestamp": datetime.datetime.utcnow()})

		self.db.all_packet.insert_one({"Switch": self.id, "Type": msg_type, "Timestamp": datetime.datetime.utcnow()})

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

	LISTEN_HOST, LISTEN_PORT = '0.0.0.0', 6653
	FORWARD_HOST, FORWARD_PORT = 'sd-lemon.naist.jp', 6633
	# FORWARD_HOST, FORWARD_PORT = 'localhost', 6653
	manager = MessageWatcher(LISTEN_HOST, LISTEN_PORT, FORWARD_HOST, FORWARD_PORT)
	manager.start()
