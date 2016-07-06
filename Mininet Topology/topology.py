from mininet.topo import Topo

class MyTopo( Topo ):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        Host1 = self.addHost('h1')
        Host2 = self.addHost('h2')
        Host3 = self.addHost('h3')
        Host4 = self.addHost('h4')
        Host5 = self.addHost('h5')
        Host6 = self.addHost('h6')
        Host7 = self.addHost('h7')
        Host8 = self.addHost('h8')
        Host9 = self.addHost('h9')
        Host10 = self.addHost('h10')
        Switch1 = self.addSwitch('s1')
        Switch2 = self.addSwitch('s2')
        Switch3 = self.addSwitch('s3')
        Switch4 = self.addSwitch('s4')
        Switch5 = self.addSwitch('s5')
        Switch6 = self.addSwitch('s6')
        Switch7 = self.addSwitch('s7')
        Switch8 = self.addSwitch('s8')
        Switch9 = self.addSwitch('s9')
        Switch10 = self.addSwitch('s10')
        Switch11 = self.addSwitch('s11')
        Switch12 = self.addSwitch('s12')
        Switch13 = self.addSwitch('s13')
        Switch14 = self.addSwitch('s14')

        # Add links
        self.addLink(Host1, Switch1)
        self.addLink(Host2, Switch2)
        self.addLink(Host3, Switch3)
        self.addLink(Host4, Switch8)
        self.addLink(Host5, Switch9)
        self.addLink(Host6, Switch1)
        self.addLink(Host7, Switch1)
        self.addLink(Host8, Switch4)
        self.addLink(Host9, Switch8)
        self.addLink(Host10, Switch14)

        self.addLink(Switch1, Switch2)
        self.addLink(Switch2, Switch3)
        self.addLink(Switch3, Switch4)
        self.addLink(Switch3, Switch5)
        self.addLink(Switch5, Switch6)
        self.addLink(Switch5, Switch7)
        self.addLink(Switch6, Switch10)
        self.addLink(Switch7, Switch8)
        self.addLink(Switch8, Switch9)
        self.addLink(Switch9, Switch11)
        self.addLink(Switch10, Switch12)
        self.addLink(Switch12, Switch13)
        self.addLink(Switch13, Switch14)


topos = { 'mytopo': ( lambda: MyTopo() ) }
