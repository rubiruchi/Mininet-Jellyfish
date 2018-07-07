#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import RemoteController,Host,Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def emptyNet():

    net = Mininet( controller=RemoteController )

    info( '*** Adding controller\n' )
    net.addController( 'c0', 
                       controller=RemoteController, 
                       ip = "127.0.0.1", 
                       port=6633 )

    info( '*** Adding hosts\n' )
    #---------subnet1---------
    h1 = net.addHost( 'h1', 
                      ip='10.0.0.1', 
                      mac='00:00:00:00:00:01',
                      defaultRoute='via 10.0.0.254')
    h2 = net.addHost( 'h2', 
                      ip='10.0.0.2',
                      mac='00:00:00:00:00:02',
                      defaultRoute='via 10.0.0.254')
    h3 = net.addHost( 'h3', 
                      ip='10.0.0.3', 
                      mac='00:00:00:00:00:03',
                      defaultRoute='via 10.0.0.254')
    #---------subnet2---------
    k4 = net.addHost( 'k4', 
                      ip='192.168.0.10', 
                      mac='00:00:00:00:00:10',
                      defaultRoute='via 192.168.0.254')
    k5 = net.addHost( 'k5',
                      ip='192.168.0.11',
                      mac='00:00:00:00:00:11',
                      defaultRoute='via 192.168.0.254')
    k6 = net.addHost( 'k6', 
                      ip='192.168.0.12', 
                      mac='00:00:00:00:00:12',
                      defaultRoute='via 192.168.0.254')
        
    info( '*** Adding switch\n' )
    s1 = net.addSwitch( 's1' )
    s2 = net.addSwitch( 's2' )
    info( '*** Creating links\n' )
    #---------subnet1---------
    net.addLink( h1, s1 )
    net.addLink( h2, s1 )
    net.addLink( h3, s1 )
    #---------subnet2---------
    net.addLink( k4, s2 )
    net.addLink( k5, s2 )
    net.addLink( k6, s2 )
    #---------switch----------
    net.addLink( s1, s2 )

    info( '*** Adding gateway\n')
    gateway = Host('gateway')
    net.addLink(s1, gateway)
    net.addLink(s2, gateway)
    gateway.intf("gateway-eth0").setIP('10.0.0.254/24')
    gateway.intf("gateway-eth1").setIP('192.168.0.254/24')
    
    info( '*** Starting network\n')
    net.start()

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
