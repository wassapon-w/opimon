import socket
import select
import threading
import struct

import datetime
import time

import logging
from binascii import hexlify, unhexlify

from ryu.ofproto import ofproto_common
from ryu.ofproto import ofproto_parser
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_protocol
from ryu.ofproto.ether import ETH_TYPE_LLDP

from ryu.lib.packet import packet, ethernet, lldp, ipv4
from ryu.lib.dpid import dpid_to_str, str_to_dpid
from ryu.ofproto import ofproto_v1_0_parser
# from ofproto import ofproto_v1_0_parser_extention

# from ryu.ofproto import ofproto_v1_0_parser
from ryu.lib import addrconv, ip, mac

from pymongo import MongoClient

from ryu.lib.mac import BROADCAST_STR

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
		self.downstream_buf = bytearray()
		self.upstream_buf = bytearray()
		self.timeloop = time.time()

		# Connect to database
		# client = MongoClient('localhost', 27017)
		# self.db = client['netspec']

		# Connect to database
		# client = MongoClient('sd-lemon.naist.jp', 9999)
		# client = MongoClient('127.0.0.1', 27017)
		client = MongoClient('mongodb://opimon:H62uTDnEtBFEiQrN1Qmktfj8XZVAuixX5YnyeA7TPIB36DDHu5KAncsJAyuqcNJqFaDVwymxHPKSGpGZ3fkgcg==@opimon.documents.azure.com:10250/?ssl=true&ssl_cert_reqs=CERT_NONE')
		self.db = client.opimon

	def run(self):
		while(self.is_alive):
			self._loop()

	def _drop_collections(self):
		self.db.flow_mods.drop()

	def _loop(self):
		# Initialization
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
				self.downstream_buf += ret
				self.downstream_buf = self._parse(self.downstream_buf, self._downstream_parse)

			if sock is self.switch_socket:
				self.upstream_buf += ret
				self.upstream_buf = self._parse(self.upstream_buf, self._upstream_parse)

		if(time.time() > self.timeloop + 60):
			self.inject_request_message()
			self.timeloop = time.time()

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
		return buf

	def inject_request_message(self):
		# print(str(self.id) + " : Sent Message")
		ofp_parser = self.datapath.ofproto_parser
		out = ofp_parser.OFPFeaturesRequest(self.datapath)
		out.serialize()
		try:
			self.switch_socket.send(out.buf)
		except:
			if(self.id != None):
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Downstream : Send monitor message)")
			else:
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Downstream : Send monitor message)")
			pass

		ofp = self.datapath.ofproto
		ofp_parser = self.datapath.ofproto_parser
		match = ofp_parser.OFPMatch()
		table_id = 0xff
		out_port = ofp.OFPP_NONE
		out = ofp_parser.OFPFlowStatsRequest(self.datapath, 0, match, table_id, out_port)
		out.serialize()
		try:
			self.switch_socket.send(out.buf)
		except:
			if(self.id != None):
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Downstream : Send monitor message)")
			else:
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Downstream : Send monitor message)")
			pass

		ofp = self.datapath.ofproto
		ofp_parser = self.datapath.ofproto_parser
		out = ofp_parser.OFPPortStatsRequest(self.datapath, 0, ofp.OFPP_NONE)
		out.serialize()
		try:
			self.switch_socket.send(out.buf)
		except:
			if(self.id != None):
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Downstream : Send monitor message)")
			else:
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Downstream : Send monitor message)")
			self._close()

		if(self.id != None):
			print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : [" + str(hex(self.id)) + "] --- Sent monitor messages")
		else:
			print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : [" + str(self.id) + "] --- Sent monitor messages")

	# Controller to Switch
	def _downstream_parse(self, pkt):
		try:
			self.switch_socket.send(pkt)
		except:
			if(self.id != None):
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Downstream)")
			else:
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Downstream)")
			self._close()
			pass

		(version, msg_type, msg_len, xid) = ofproto_parser.header(pkt)

		# Controller command messages
		if msg_type == ofproto_v1_0.OFPT_FLOW_MOD:
			msg = ofproto_v1_0_parser.OFPFlowMod.parser(self.datapath, version, msg_type, msg_len, xid, pkt)

			# print(str(self.id) + " : Receive Flow Mod Message")

			# Write to database
			# db_message = {"switch": hex(self.id),
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
			# 					  "dl_src": mac.haddr_to_str(msg.match.dl_src),
			# 					  "dl_dst": mac.haddr_to_str(msg.match.dl_dst),
			# 					  "dl_vlan": msg.match.dl_vlan,
			# 					  "dl_vlan_pcp": msg.match.dl_vlan_pcp,
			# 					  "dl_type": msg.match.dl_type,
			# 					  "nw_tos": msg.match.nw_tos,
			# 					  "nw_proto": msg.match.nw_proto,
			# 					  "nw_src": ip.ipv4_to_str(msg.match.nw_src),
			# 					  "nw_dst": ip.ipv4_to_str(msg.match.nw_dst),
			# 					  "tp_src": msg.match.tp_src,
			# 					  "tp_dst": msg.match.tp_dst
			# 				  },
			# 				  "cookie": msg.cookie,
			# 				  "command": msg.command,
			# 				  "idle_timeout": msg.idle_timeout,
			# 				  "hard_timeout": msg.hard_timeout,
			# 				  "priority": msg.priority,
			# 				  "buffer_id": msg.buffer_id,
			# 				  "out_port": msg.out_port,
			# 				  "flags": msg.flags,
			# 				  "actions": []
			# 			  },
			# 			  "timestamp": datetime.datetime.utcnow()}
			#
			# for action in msg.actions:
			# 	db_message["message"]["actions"].append(vars(action));

			# print(db_message)

			# try:
			# 	self.db.flow_mods.insert_one(db_message)
			# 	if(self.id != None):
			# 		print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : [" + str(hex(self.id)) + "] --- Received FlowMod message")
			# 	else:
			# 		print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : [" + str(self.id) + "] --- Received FlowMod message")
			# except:
			# 	if(self.id != None):
			# 		print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
			# 	else:
			# 		print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")
			# 	pass

	# Switch to Controller
	def _upstream_parse(self, pkt):
		(version, msg_type, msg_len, xid) = ofproto_parser.header(pkt)

		# Switch configuration messages
		if msg_type == ofproto_v1_0.OFPT_FEATURES_REPLY:
			msg = ofproto_v1_0_parser.OFPSwitchFeatures.parser(self.datapath, version, msg_type, msg_len, xid, pkt)
			match = ofproto_v1_0_parser.OFPMatch(dl_type=ETH_TYPE_LLDP, dl_dst=lldp.LLDP_MAC_NEAREST_BRIDGE)
			cookie = 0
			command = ofproto_v1_0.OFPFC_ADD
			idle_timeout = hard_timeout = 0
			priority = 0
			buffer_id = ofproto_v1_0.OFP_NO_BUFFER
			out_port = ofproto_v1_0.OFPP_NONE
			flags = 0
			actions = [ofproto_v1_0_parser.OFPActionOutput(ofproto_v1_0.OFPP_CONTROLLER)]
			mod = ofproto_v1_0_parser.OFPFlowMod(self.datapath, match, cookie, command, idle_timeout, hard_timeout, priority, buffer_id, out_port, flags, actions)
			mod.serialize()

			self.id = msg.datapath_id
			self.ports = msg.ports

			# print(str(self.id) + " : Receive Features Reply Message")

			# print(msg)

			for port in self.ports.values():
				db_message = {"switch_id": hex(self.id),
							  "port_no": port.port_no,
							  "hw_addr": port.hw_addr,
							  "timestamp": datetime.datetime.utcnow()}

				try:

					self.db.switch_port.insert_one(db_message)
				except:
					if(self.id != None):
						print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
					else:
						print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")

				pkt_lldp = packet.Packet()

				dst = BROADCAST_STR
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

				try:
					self.switch_socket.send(out.buf)
				except:
					if(self.id != None):
						print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Downstream : LLDP Message)")
					else:
						print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Downstream : LLDP Message)")
					self._close()
					pass

		elif msg_type == ofproto_v1_0.OFPT_STATS_REPLY:
			msg = ofproto_v1_0_parser.OFPPortStatsReply.parser(self.datapath, version, msg_type, msg_len, xid, pkt)
			if(type(msg) is ofproto_v1_0_parser.OFPFlowStatsReply):
				# print(str(self.id) + " : Receive Flow Stats Message")
				# print(msg.body)

				for flow in msg.body:
					db_message = {"switch": hex(self.id),
								  "message": {
									  "header": {
										  "version": msg.version,
										  "type": msg.msg_type,
										  "length": msg.msg_len,
										  "xid": msg.xid
									  },
									  "match": {
										  "wildcards": flow.match.wildcards,
										  "in_port": flow.match.in_port,
										  "dl_src": mac.haddr_to_str(flow.match.dl_src),
										  "dl_dst": mac.haddr_to_str(flow.match.dl_dst),
										  "dl_vlan": flow.match.dl_vlan,
										  "dl_vlan_pcp": flow.match.dl_vlan_pcp,
										  "dl_type": flow.match.dl_type,
										  "nw_tos": flow.match.nw_tos,
										  "nw_proto": flow.match.nw_proto,
										  "nw_src": ip.ipv4_to_str(flow.match.nw_src),
										  "nw_dst": ip.ipv4_to_str(flow.match.nw_dst),
										  "tp_src": flow.match.tp_src,
										  "tp_dst": flow.match.tp_dst
									  },
									  "cookie": flow.cookie,
									  "idle_timeout": flow.idle_timeout,
									  "hard_timeout": flow.hard_timeout,
									  "priority": flow.priority,
									  "flags": msg.flags,
									  "actions": []
								  },
								  "timestamp": datetime.datetime.utcnow()}

					for action in flow.actions:
						db_message["message"]["actions"].append(vars(action));

					try:
						self.db.flow_mods.insert_one(db_message)
					except:
						if(self.id != None):
							print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
						else:
							print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")
						pass

			if(type(msg) is ofproto_v1_0_parser.OFPPortStatsReply):
				# print(str(self.id) + " : Receive Port Stats Message")
				# print(msg.body)

				for port in msg.body:
					# print(port)
					db_message = {"switch": hex(self.id),
								  "port_no": port.port_no,
								  "rx_packets": port.rx_packets,
								  "tx_packets": port.tx_packets,
								  "rx_bytes": port.rx_bytes,
								  "tx_bytes": port.tx_bytes,
								  "rx_dropped": port.rx_dropped,
								  "tx_dropped": port.tx_dropped,
								  "rx_errors": port.rx_errors,
								  "tx_errors": port.tx_errors,
								  "rx_frame_err": port.rx_frame_err,
								  "rx_over_err": port.rx_over_err,
								  "rx_crc_err": port.rx_crc_err,
								  "collisions": port.collisions,
								  "timestamp": datetime.datetime.utcnow()}

					try:
						self.db.port_stats.insert_one(db_message)
					except:
						if(self.id != None):
							print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
						else:
							print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")

				pass

		# Asynchronous messages
		elif msg_type == ofproto_v1_0.OFPT_PACKET_IN:
			msg = ofproto_v1_0_parser.OFPPacketIn.parser(self.datapath, version, msg_type, msg_len, xid, pkt)
			pkt_msg = packet.Packet(msg.data)

			if pkt_msg.get_protocol(ethernet.ethernet).ethertype == ETH_TYPE_LLDP:
				lldp_msg = pkt_msg.get_protocol(lldp.lldp)

				if lldp_msg != None:
					if lldp_msg.tlvs[3].tlv_info == "ProxyTopologyMonitorLLDP":

						(port,) = struct.unpack('!I', lldp_msg.tlvs[1].port_id)
						switch_src = str_to_dpid(lldp_msg.tlvs[0].chassis_id[5:])

						# print(str(self.id) + " : Receive Proxy LLDP Packet")
						# print(lldp_msg)

						# Write to database
						try:
							self.db.topology.insert_one({"switch_dst": hex(self.id),
													 	 "port_dst": port,
													 	 "switch_src": hex(switch_src),
													 	 "port_src": msg.in_port,
													 	 "timestamp": datetime.datetime.utcnow()})
						except:
							if(self.id != None):
								print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
							else:
								print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")

						return

					elif lldp_msg.tlvs[3].tlv_info != "ProxyTopologyMonitorLLDP":
						# print(lldp_msg)
						# print("Controller LLDP packet")
						pass

		try:
			self.controller_socket.send(pkt)
		except:
			if(self.id != None):
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Upstream)")
			else:
				print(datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Upstream)")
			self._close()
			pass

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
	print("Monitor is running.")

	LISTEN_HOST, LISTEN_PORT = '0.0.0.0', 6653
	FORWARD_HOST, FORWARD_PORT = 'sd-lemon.naist.jp', 3000
	# FORWARD_HOST, FORWARD_PORT = 'localhost', 6733
	manager = MessageWatcher(LISTEN_HOST, LISTEN_PORT, FORWARD_HOST, FORWARD_PORT)
	manager.start()
