from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

class L2Switch(app_manager.RyuApp):
	def __init__(self, *args, **kwargs):
		super(L2Switch, self).__init__(*args, **kwargs)
		self.portTable = {}

	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def packet_in_handler(self, ev):

		# Read packet info.
		msg = ev.msg
		dp = msg.datapath
		ofp = dp.ofproto
		ofp_parser = dp.ofproto_parser

		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocols(ethernet.ethernet)[0]

		dataPathID = dp.id
		inPort = msg.in_port

		sourceMAC = eth.src
		destinationMAC = eth.dst

		self.portTable.setdefault(dataPathID, {})
		self.portTable[dataPathID][sourceMAC] = inPort

		if destinationMAC in self.portTable[dataPathID]:
			outPort = self.portTable[dataPathID][destinationMAC]
		else:
			outPort = ofp.OFPP_FLOOD

		self.logger.info("Switch ID : %s / Source : %s (%s) / Destination : %s (%s)", dataPathID, sourceMAC, inPort, destinationMAC, outPort)

		actions = [ofp_parser.OFPActionOutput(outPort)]

		if outPort != ofp.OFPP_FLOOD:
			match = ofp_parser.OFPMatch(in_port=inPort, dl_dst=destinationMAC)
			mod = ofp_parser.OFPFlowMod(datapath=dp, priority=1, match=match, actions=actions)
			dp.send_msg(mod)

		if msg.buffer_id == ofp.OFP_NO_BUFFER:
			data = msg.data
		else:
			data = None

		out = ofp_parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port, actions=actions, data=data)

		dp.send_msg(out)
