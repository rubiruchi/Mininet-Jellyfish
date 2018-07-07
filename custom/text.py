from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import Intf
from mininet.util import dumpNodeConnections

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        
	h1 = self.addHost( 'h1' )
	h2 = self.addHost( 'h2' )
	h3 = self.addHost( 'h3' )
	h4 = self.addHost( 'h4' )
	
	#Add switches
	
	s1 = self.addSwitch( 's1' )
	s2 = self.addSwitch( 's2' )
	
	#leftHost = self.addHost( 'h1' )
        #rightHost = self.addHost( 'h2' )
        #leftSwitch = self.addSwitch( 's3' )
        #rightSwitch = self.addSwitch( 's4' )

        # Add links
        
	self.addLink( s1, s2 )

	self.addLink( h1 , s1 )
	self.addLink( h2 , s1 )
	self.addLink( h3 , s2 )
	self.addLink( h4 , s2 )


	#Add Flow
	
#	info("Adding Flow \n")


	#self.addLink( leftHost, leftSwitch )
        #self.addLink( leftSwitch, rightSwitch )
        #self.addLink( rightSwitch, rightHost )


topos = { 'mytopo': ( lambda: MyTopo() ) }

