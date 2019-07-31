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
        Switch15 = self.addSwitch('s15')

        # Core Switch
        self.addLink(Switch1, Switch2)
        self.addLink(Switch2, Switch3)

        # Edge Switch
        self.addLink(Switch1, Switch4)
        self.addLink(Switch1, Switch5)
        self.addLink(Switch2, Switch6)
        self.addLink(Switch2, Switch7)
        self.addLink(Switch2, Switch8)
        self.addLink(Switch3, Switch9)
        self.addLink(Switch3, Switch10)

        self.addLink(Switch5, Switch11)
        self.addLink(Switch6, Switch12)
        self.addLink(Switch6, Switch13)
        self.addLink(Switch8, Switch14)
        self.addLink(Switch9, Switch15)

        # Host
        self.addLink(Host1, Switch11)
        self.addLink(Host2, Switch11)
        self.addLink(Host3, Switch12)
        self.addLink(Host4, Switch12)
        self.addLink(Host5, Switch13)
        self.addLink(Host6, Switch14)
        self.addLink(Host7, Switch15)

topos = { 'mytopo': ( lambda: MyTopo() ) }
