from ryu.ofproto import ofproto_v1_0_parser as ofproto_parser
from ryu.ofproto import ofproto_v1_0 as ofproto

import struct
import binascii

import logging


class OFPPacketOut(ofproto_parser.OFPPacketOut):
	def __init__(self, datapath):
		super(OFPPacketOut, self).__init__(datapath)

	@classmethod
	def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
		msg = super(OFPPacketOut, cls).parser(
			datapath, version, msg_type, msg_len, xid, buf)
		(msg.buffer_id,
		 msg.in_port,
		 msg.actions_len) = struct.unpack_from(
			ofproto.OFP_PACKET_OUT_PACK_STR,
			msg.buf, ofproto.OFP_HEADER_SIZE)
		msg.actions = []

		_actions_len = msg.actions_len
		_actions_buf = buf[ofproto.OFP_PACKET_OUT_SIZE:]
		_offset = 0

		while _actions_len > 0:
			action = ofproto_parser.OFPAction.parser(_actions_buf, _offset)
			msg.actions.append(action)
			_actions_len -= action.len
			_offset += action.len

		return msg


class OFPFlowMod(ofproto_parser.OFPFlowMod):
	def __init__(self, datapath, match=None, cookie=None, command=None, 
				 idle_timeout=0, hard_timeout=0,
				 priority=ofproto.OFP_DEFAULT_PRIORITY,
				 buffer_id=0xffffffff, out_port=ofproto.OFPP_NONE,
				 flags=0, actions=None):
		super(OFPFlowMod, self).__init__(datapath, match, cookie, command,
										 idle_timeout, hard_timeout,
										 priority,
										 buffer_id, out_port,
										 flags, actions)
		self.match = match
		self.cookie = cookie
		self.command = command
		self.idle_timeout = idle_timeout
		self.hard_timeout = hard_timeout
		self.priority = priority
		self.buffer_id = buffer_id
		self.out_port = out_port
		self.flags = flags
		self.actions = actions


	@classmethod
	def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
		msg = super(OFPFlowMod, cls).parser(
			datapath, version, msg_type, msg_len, xid, buf)
		msg.match = ofproto_parser.OFPMatch.parse(msg.buf,
												  ofproto.OFP_HEADER_SIZE)

		LOG = logging.getLogger('netspec.ofproto.ofproto_v1_0_extention.OFPFlowMod')
#        LOG.debug("wildcards %d, in_port %d, dl_src %d, dl_dst %d, dl_vlan %d, dl_vlan_pcp %d, dl_type %d, nw_tos %d, nw_proto %d, nw_src %d, nw_dst %d, tp_src %d, tp_dst %d",
#                  msg.match.wildcards,
#                  msg.match.in_port,
#                  msg.match.dl_src,
#                  msg.match.dl_dst,
#                  msg.match.dl_vlan,
#                  msg.match.dl_vlan_pcp,
#                  msg.match.dl_type,
#                  msg.match.nw_tos,
#                  msg.match.nw_proto,
#                  msg.match.nw_src,
#                  msg.match.nw_dst,
#                  msg.match.tp_src,
#                  msg.match.tp_dst)
		LOG.debug("in_port %d", msg.match.in_port)

		(msg.cookie,
		 msg.command,
		 msg.idle_timeout,
		 msg.hard_timeout,
		 msg.priority,
		 msg.buffer_id,
		 msg.out_port,
		 msg.flags) = struct.unpack_from(
			ofproto.OFP_FLOW_MOD_PACK_STR0,
			msg.buf, ofproto.OFP_HEADER_SIZE+ofproto.OFP_MATCH_SIZE)
		msg.actions = []

		_actions_len = msg_len - ofproto.OFP_FLOW_MOD_SIZE
		_actions_buf = buf[ofproto.OFP_FLOW_MOD_SIZE:]
		_offset = 0

		while _actions_len > 0:
			action = ofproto_parser.OFPAction.parser(_actions_buf, _offset)
			msg.actions.append(action)
			_actions_len -= action.len
			_offset += action.len

		return msg
