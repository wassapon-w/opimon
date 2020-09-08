import socket
import select
import threading
import multiprocessing
import struct
import argparse
import sys

from collections import deque

import datetime
import time

import logging
from binascii import hexlify, unhexlify

import cProfile
import pstats
import io
import line_profiler

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
from ryu.lib.mac import BROADCAST_STR

from pymongo import MongoClient
from pprint import pprint

# import log

# profile = line_profiler.LineProfiler()

LOG = logging.getLogger('OpenFlow Monitor')
upstream_queue = multiprocessing.Queue()
downstream_queue = multiprocessing.Queue()
message_queue = multiprocessing.Queue()

class MessageParserAgentThread(multiprocessing.Process):
	def __init__(self):
		super(MessageParserAgentThread, self).__init__()

		self.datapath = ofproto_protocol.ProtocolDesc(version=0x01)
		self.id = None

	def run(self):
		client = MongoClient('127.0.0.1', 27017)
		self.db = client.opimon

		while(True):
			# print("MessageParserAgentThread (" + str(multiprocessing.current_process().pid) + "): " + str(message_queue.qsize()))

			pkt = message_queue.get(True, None)
			self._message_parse(pkt)

	def _message_parse(self, pkt):
		(version, msg_type, msg_len, xid) = ofproto_parser.header(pkt)

		# Controller command messages
		if msg_type == ofproto_v1_0.OFPT_FLOW_MOD:
			msg = ofproto_v1_0_parser.OFPFlowMod.parser(self.datapath, version, msg_type, msg_len, xid, pkt)

			# print(str(self.id) + " : Receive Flow Mod Message")

			# Write to database
			db_message = {"switch": hex(self.id),
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
								  "dl_src": mac.haddr_to_str(msg.match.dl_src),
								  "dl_dst": mac.haddr_to_str(msg.match.dl_dst),
								  "dl_vlan": msg.match.dl_vlan,
								  "dl_vlan_pcp": msg.match.dl_vlan_pcp,
								  "dl_type": msg.match.dl_type,
								  "nw_tos": msg.match.nw_tos,
								  "nw_proto": msg.match.nw_proto,
								  "nw_src": ip.ipv4_to_str(msg.match.nw_src),
								  "nw_dst": ip.ipv4_to_str(msg.match.nw_dst),
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
				db_message["message"]["actions"].append(vars(action))

			# print(db_message)

			try:
				self.db.flow_mods.insert_one(db_message)
				# pass
				# if(self.id != None):
				# 	print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : [" + str(hex(self.id)) + "] --- Received FlowMod message")
				# else:
				# 	print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : [" + str(self.id) + "] --- Received FlowMod message")
			except:
				if(self.id != None):
					print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
				else:
					print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")
				pass

		# Switch configuration messages
		elif msg_type == ofproto_v1_0.OFPT_FEATURES_REPLY:
			# print("Reply xid: " + hex(xid))
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
						print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
					else:
						print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")

		elif msg_type == ofproto_v1_0.OFPT_STATS_REPLY:
			msg = ofproto_v1_0_parser.OFPPortStatsReply.parser(self.datapath, version, msg_type, msg_len, xid, pkt)
			if(type(msg) is ofproto_v1_0_parser.OFPFlowStatsReply):
				# print(str(self.id) + " : Receive Flow Stats Message")
				# print(msg)

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
						db_message["message"]["actions"].append(vars(action))

					try:
						self.db.flow_stats.insert_one(db_message)
					except:
						if(self.id != None):
							print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
						else:
							print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")
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
							print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
						else:
							print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")

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
								print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Failed to write data into database")
							else:
								print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Failed to write data into database")

						return

					elif lldp_msg.tlvs[3].tlv_info != "ProxyTopologyMonitorLLDP":
						# print(lldp_msg)
						# print("Controller LLDP packet")
						pass

class MessageWatcherAgentThread(multiprocessing.Process):
	def __init__(self, switch_socket, controller_host, controller_port):
		super(MessageWatcherAgentThread, self).__init__()

		self.controller_socket = socket.socket()
		self.controller_socket.connect((controller_host, controller_port))
		# self.controller_socket.setblocking(0)
		# self.controller_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.switch_socket = switch_socket
		# self.switch_socket.setblocking(0)
		# self.switch_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.is_alive = True
		self.datapath = ofproto_protocol.ProtocolDesc(version=0x01)
		self.id = None
		self.downstream_buf = bytearray()
		self.upstream_buf = bytearray()
		self.timeloop = time.time()

		self.controller_buffer = deque()
		self.switch_buffer = deque()

		self.recv_socks = [self.controller_socket, self.switch_socket]
		self.send_socks = set([])

	def profile_run(self):
		# cProfile.runctx('self.run()', globals(), locals(), 'prof-%d.prof' % int(multiprocessing.current_process().pid))

		prof = line_profiler.LineProfiler()
		prof.add_function(self._loop)
		prof.add_function(self._parse)
		prof.add_function(self._downstream_sender)
		prof.add_function(self._upstream_sender)
		prof.add_function(self._downstream_buffer)
		prof.add_function(self._upstream_buffer)
		prof.runcall(self.run_with_profile, prof)
		
	def run_with_profile(self, prof):
		while(self.is_alive):
			self._loop()
			# prof.print_stats()
			prof.dump_stats('prof-%d.lprof' % int(multiprocessing.current_process().pid))

	def run(self):
		while(self.is_alive):
			self._loop()

	def _drop_collections(self):
		self.db.flow_mods.drop()

	def _loop(self):
		# Wait for receive
		rsocks, wsocks, esocks = select.select(self.recv_socks, self.send_socks, [])

		for sock in rsocks:

			# Receive packet
			ret = sock.recv(2048)

			if not ret:
				self._close()
				break

			if sock is self.controller_socket:
				self.downstream_buf += ret
				# if self.switch_socket in wsocks:
				# 	self.downstream_buf = self._parse(self.downstream_buf, self._downstream_sender)
				# else:
				self.downstream_buf = self._parse(self.downstream_buf, self._downstream_buffer)

			if sock is self.switch_socket:
				self.upstream_buf += ret
				# if self.controller_socket in wsocks:
				# 	self.upstream_buf = self._parse(self.upstream_buf, self._upstream_sender)
				# else:
				self.upstream_buf = self._parse(self.upstream_buf, self._upstream_buffer)

		for sock in wsocks:
			if sock is self.controller_socket:
				# while(self.controller_buffer):
				self._upstream_sender(self.controller_buffer.popleft())
				if not self.controller_buffer:
					self.send_socks.discard(self.controller_socket)

			if sock is self.switch_socket:
				# while(self.switch_buffer):
				self._downstream_sender(self.switch_buffer.popleft())
				if not self.switch_buffer:
					self.send_socks.discard(self.switch_socket)

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
		out.xid = 0xffffffff
		out.serialize()
		# self.parse_pkt(out, "FeaturesRequest")
		try:
			self.switch_socket.send(out.buf)
		except:
			if(self.id != None):
				print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Downstream : Send monitor message)")
			else:
				print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Downstream : Send monitor message)")
			pass

		ofp = self.datapath.ofproto
		ofp_parser = self.datapath.ofproto_parser
		match = ofp_parser.OFPMatch()
		table_id = 0xff
		out_port = ofp.OFPP_NONE
		out = ofp_parser.OFPFlowStatsRequest(self.datapath, 0, match, table_id, out_port)
		out.xid = 0xffffffff
		out.serialize()
		# self.parse_pkt(out, "FlowStatsRequest")
		try:
			self.switch_socket.send(out.buf)
		except:
			if(self.id != None):
				print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Downstream : Send monitor message)")
			else:
				print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Downstream : Send monitor message)")
			pass

		ofp = self.datapath.ofproto
		ofp_parser = self.datapath.ofproto_parser
		out = ofp_parser.OFPPortStatsRequest(self.datapath, 0, ofp.OFPP_NONE)
		out.xid = 0xffffffff
		out.serialize()
		# self.parse_pkt(out, "PortStatsRequest")
		try:
			self.switch_socket.send(out.buf)
		except:
			if(self.id != None):
				print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Downstream : Send monitor message)")
			else:
				print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Downstream : Send monitor message)")
			# self._close()

		if(self.id != None):
			print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : [" + str(hex(self.id)) + "] --- Sent monitor messages")
		else:
			print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : [" + str(self.id) + "] --- Sent monitor messages")

	def parse_pkt(self, pkt, type):
		# print(pkt)
		print("Request " + hex(pkt.msg_type) + "(" + type + ") " + "xid: " + hex(pkt.xid))

	# Controller to Switch
	def _downstream_sender(self, pkt):
		# self.switch_buffer.append(pkt)

		try:
			self.switch_socket.send(pkt)
		except Exception as e:
			print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR (Downstream) --- " + str(sys.exc_info()[0]) + " " + str(e))
			# if(self.id != None):
			# 	print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] (Downstream) --- " + str(sys.exc_info()[0]) + " " + str(e))
			# else:
			# 	print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] (Downstream) --- " + str(sys.exc_info()[0]) + " " + str(e))
			# self._close()
			# pass

		# message_queue.put(pkt)

	# Switch to Controller
	def _upstream_sender(self, pkt):
		# self.controller_buffer.append(pkt)

		(version, msg_type, msg_len, xid) = ofproto_parser.header(pkt)

		# if(self.id != None):
		# 	print("[" + str(hex(self.id)) + "] " + str(msg_type))

		if(xid == 0xffffffff):
			# self._upstream_collector(pkt)
			pass
		else:
			try:
				self.controller_socket.send(pkt)
			except Exception as e:
				print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR (Upstream) --- " + str(sys.exc_info()[0]) + " " + str(e))
			# if(self.id != None):
			# 	print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] (Upstream) --- " + str(sys.exc_info()[0]) + " " + str(e))
			# else:
			# 	print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] (Upstream) --- " + str(sys.exc_info()[0]) + " " + str(e))
			# self._close()
			# pass
			# self._upstream_collector(pkt)

	def _downstream_buffer(self, pkt):
		self.switch_buffer.append(pkt)
		self.send_socks.add(self.switch_socket)

	# Switch to Controller
	def _upstream_buffer(self, pkt):
		self.controller_buffer.append(pkt)
		self.send_socks.add(self.controller_socket)
	
	def _upstream_collector(self, pkt):
		message_queue.put(pkt)
		(version, msg_type, msg_len, xid) = ofproto_parser.header(pkt)

		# print(str(hex(xid)) + " - " + str(msg_type))

		# Switch configuration messages
		if msg_type == ofproto_v1_0.OFPT_FEATURES_REPLY:
			# print("Reply xid: " + hex(xid))
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
				pkt_lldp = packet.Packet()

				dst = BROADCAST_STR
				src = port.hw_addr
				ethertype = ETH_TYPE_LLDP
				eth_pkt = ethernet.ethernet(dst, src, ethertype)
				pkt_lldp.add_protocol(eth_pkt)

				tlv_chassis_id = lldp.ChassisID(
					subtype=lldp.ChassisID.SUB_LOCALLY_ASSIGNED,
					chassis_id=b'dpid:%s' % dpid_to_str(self.id).encode())

				tlv_port_id = lldp.PortID(subtype=lldp.PortID.SUB_PORT_COMPONENT,
										  port_id=struct.pack('!I', port.port_no))

				tlv_ttl = lldp.TTL(ttl=120)
				tlv_desc = lldp.PortDescription(port_description=b"ProxyTopologyMonitorLLDP")
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
						print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(hex(self.id)) + "] --- Broken Pipe (Downstream : LLDP Message)")
					else:
						print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : ERROR [" + str(self.id) + "] --- Broken Pipe (Downstream : LLDP Message)")
					# self._close()
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
		# self.threads = []
		self.connection_list = []
		self.parser_list = []

		args_parser = argparse.ArgumentParser(description='Additional Options')
		args_parser.add_argument('-p', action='store_true', dest="profile", default=False)
		self.args = args_parser.parse_args()

		if(self.args.profile):
			print("Enable profiler")

	def _handle(self, sock):
		# thread = MessageWatcherAgentThread(sock, self.forward_host, self.forward_port)
		# thread.start()
		# self.threads.append(thread)

		print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + " : [" + str(len(self.connection_list)) + "] Receiving new connection...")
		connection = MessageWatcherAgentThread(sock, self.forward_host, self.forward_port)
		if(self.args.profile):
			connection_process = multiprocessing.Process(target=connection.profile_run)
		else:
			connection_process = multiprocessing.Process(target=connection.run)
		connection_process.start()
		self.connection_list.append(connection_process)

	def start(self):
		# self.logger.info("Running")
		self.run()

	def run(self):
		for i in range(5):
			message_parser = MessageParserAgentThread()
			message_parser_process = multiprocessing.Process(target=message_parser.run)
			message_parser_process.start()
			self.parser_list.append(message_parser_process)

		try:
			while(True):
				self._loop()
		except KeyboardInterrupt:
			print("Exiting...")
			for connection in self.connection_list:
				connection.terminate()
			for parser in self.parser_list:
				parser.terminate()
			print("Terminated")

	def _loop(self):
		conn, addr = self.listen_socket.accept()
		self._handle(conn)

if __name__ == '__main__':

	# log.init_log()
	print("Opimon (Monitoring Tool) is running.")

	LISTEN_HOST, LISTEN_PORT = '0.0.0.0', 6753
	# FORWARD_HOST, FORWARD_PORT = 'sd-lemon.naist.jp', 3000
	FORWARD_HOST, FORWARD_PORT = 'localhost', 6733
	manager = MessageWatcher(LISTEN_HOST, LISTEN_PORT, FORWARD_HOST, FORWARD_PORT)
	manager.start()
