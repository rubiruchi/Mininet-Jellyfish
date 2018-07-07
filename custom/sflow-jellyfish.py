#!/usr/bin/python
"""@package topologies

Jellyfish Topology.

@author Patrick Costello (pcostell@stanford.edu)
@author Lynn Cuthriell (lcuth@stanford.edu)
"""
from mininet.net import Mininet
from mininet.util import quietRun
from requests import put
from json import dumps
from subprocess import call, check_output
from os import listdir
import re
import socket

#=======================================

import random

from mininet.log import lg

from ripl.dctopo import StructuredTopo
from ripl.dctopo import StructuredNodeSpec
from ripl.dctopo import StructuredEdgeSpec
from mininet.link import TCLink

#=======================================

from mininet.topo import Topo
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel

class JellyfishNodeID(object):
  '''Topo node identifier.'''

  def __init__(self, switch_id=None, host_id=None, dpid=None, name=None):
    '''Init.

    @param switch_id
    @param host_id
    @param dpid dpid
    '''
    if name is not None:
      if name[0] == 'h':
        self.switch_id = int(name[1:])
        self.host_id = int(name[1:])
      elif name[0] == 's':
        self.switch_id = int(name[1:])
        self.host_id = 255
      self.dpid = (self.switch_id << 8) + self.host_id
    elif dpid is not None:
      self.switch_id = (dpid & 0xff00) >> 8
      self.host_id = (dpid & 0xff)
      self.dpid = dpid
    else:
      self.host_id = host_id
      self.switch_id = switch_id
      self.dpid = ((self.switch_id) << 8) + (self.host_id)

  def __str__(self):
    '''String conversion.

    @return str dpid as string
    '''
    if self.host_id == 255:
      return "s%d" % self.switch_id
    else:
      return "h%d" % self.host_id

  def name_str(self):
    '''Name conversion.

    @return name name as string
    '''
    return str(self)

  def ip_str(self):
    '''Name conversion.

    @return ip ip as string
    '''
    mid = (self.dpid & 0xff00) >> 8
    lo = self.dpid & 0xff
    return "10.0.%i.%i" % (mid, lo)

  def mac_str(self):
    mid = (self.dpid & 0xff00) >> 8
    lo = self.dpid & 0xff
    return "00:00:00:00:%02x:%02x" % (mid, lo)


# Topology to be instantiated in Mininet
class JellyfishTopo(StructuredTopo):
  "Jellyfish Topology."

  LAYER_EDGE = 2
  LAYER_HOST = 3

  def def_nopts(self, layer, name=None):
    '''Return default dict for a FatTree topo.

    @param layer layer of node
    @param name name of node
    @return d dict with layer key/val pair, plus anything else (later)
    '''
    d = {'layer': layer}
    if name:
      id = self.id_gen(name=name)
      # For hosts only, set the IP
      if layer == self.LAYER_HOST:
        d.update({'ip': id.ip_str()})
        d.update({'mac': id.mac_str()})
      d.update({'dpid': "%016x" % id.dpid})
    return d

  def __init__(self, seed=0, switches=10, nodes=6, ports_per_switch=4,
               hosts_per_switch=1, bw=100):
    # Add default members to class.
    self.bw = bw
    self.id_gen = JellyfishNodeID
    random.seed(seed)

    edge_specs = [StructuredEdgeSpec(bw)] * 3
    node_specs = [StructuredNodeSpec(ports_per_switch - hosts_per_switch,
                                     hosts_per_switch, bw, bw, 'edge'),
                  StructuredNodeSpec(1, 0, bw, None, 'host'),
                 ]

    super(JellyfishTopo, self).__init__(node_specs, edge_specs)

    self.create_topology(switches, nodes, ports_per_switch, hosts_per_switch)

  def not_fully_connected(self, switch_list, link_list):
    for i in range(len(switch_list)):
      switch = switch_list[i]
      for j in range(i + 1, len(switch_list)):
        switch2 = switch_list[j]
        link = (switch, switch2)
        if link not in link_list and (switch2, switch) not in link_list:
          return True
    return False

  def addHosts(self, switches, nodes, ports_per_switch, hosts_per_switch):
    switch_num = 1
    host_list = []
    for num in range(0, nodes):
      host_id = self.id_gen(num+1, num+1).name_str()
      host_opts = self.def_nopts(self.LAYER_HOST, host_id)
      h = self.addHost(host_id, **host_opts)
      lg.debug("Adding host: %s\n" % (host_id))
      host_list.append(h)
      if num % hosts_per_switch == 0:
        switch_id = self.id_gen(switch_num, 255).name_str()
        switch_opts = self.def_nopts(self.LAYER_EDGE, switch_id)
        switch = self.addSwitch(switch_id, **switch_opts)
        lg.debug("Adding switch: %s\n" % (switch_id))
        for host in host_list:
          self.addLink(host, switch, cls=TCLink, bw=self.bw)
          lg.debug("Adding link: %s to %s\n" % (str(host), str(switch)))
        host_list = []
        switch_num += 1

    for num in range(nodes / hosts_per_switch, switches):
      switch_id = self.id_gen(num+1, 255).name_str()
      lg.debug("Adding switch: %s\n" % (switch_id))
      switch_opts = self.def_nopts(self.LAYER_EDGE, switch_id)
      switch = self.addSwitch(switch_id, **switch_opts)

  def count_links_with_switch(self, switch, link_list):
    count = 0
    for link in link_list:
      if switch in link:
        count += 1
    return count

  def up_nodes(self, name):
    '''Return edges one layer higher (closer to core).

    @param name name

    @return names list of names
    '''
    return [n for n in self.g[name] if self.isSwitch(n)]

  def down_nodes(self, name):
    '''Return edges one layer higher (closer to hosts).

    @param name name
    @return names list of names
    '''
    layer = self.layer(name) + 1
    nodes = [n for n in self.g[name] if self.layer(n) == layer]
    return nodes

  def switch_is_fully_connected(self, switch, links, switches):
    for s in switches:
      if s == switch:
        continue
      if (switch, s) not in links or (s, switch) not in links:
        return False
    return True

  def create_topology(self, switches, nodes, ports_per_switch, hosts_per_switch):

    self.addHosts(switches, nodes, ports_per_switch, hosts_per_switch)
    switch_list = list(self.switches())
    added_links = []
    while len(switch_list) > 1 and self.not_fully_connected(switch_list, added_links):
      switch = random.choice(switch_list)
      switch2 = random.choice(switch_list)
      if switch == switch2:
        continue
      link = (switch, switch2)
      if link in added_links or (switch2, switch) in added_links:
        continue
      added_links.append(link)
      if (self.count_links_with_switch(switch, added_links) == ports_per_switch or
         self.switch_is_fully_connected(switch, added_links, switch_list)):
        switch_list.remove(switch)
      if (self.count_links_with_switch(switch2, added_links) == ports_per_switch or
         self.switch_is_fully_connected(switch2, added_links, switch_list)):
        switch_list.remove(switch2)

    print added_links
    print switch_list
    while True:
      completed = True
      for switch in switch_list:
        if self.switch_is_fully_connected(switch, added_links, switch_list):
          continue
        if self.count_links_with_switch(switch, added_links) < (ports_per_switch-1):
          completed = False
          link = random.choice(added_links)
          if switch == link [0] or switch == link[1]:
            continue
          new_link1 = (switch, link[0])
          new_link2 = (switch, link[1])
          added_links.remove(link)
          added_links.append(new_link1)
          added_links.append(new_link2)
      if completed:
        break

    for link in added_links:
      self.addLink(link[0], link[1], cls=TCLink, bw=self.bw)

  #def run(self):
  #  net = Mininet(self)
  #  net.start()

topos = {'jellyfish': JellyfishTopo}

#-=======================================////////

collector = '127.0.0.1'
sampling = 10
polling = 3

def getIfInfo(ip):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect((ip, 0))
  ip = s.getsockname()[0]
  ifconfig = check_output(['ifconfig'])
  ifs = re.findall(r'^(\S+).*?inet addr:(\S+).*?', ifconfig, re.S|re.M)
  for entry in ifs:
    if entry[1] == ip:
      return entry

def configSFlow(net,collector,ifname):
  print "*** Enabling sFlow:"
  sflow = 'ovs-vsctl -- --id=@sflow create sflow agent=%s target=%s sampling=%s polling=%s --' % (ifname,collector,sampling,polling)
  for s in net.switches:
    sflow += ' -- set bridge %s sflow=@sflow' % s
  print ' '.join([s.name for s in net.switches])
  quietRun(sflow)

def sendTopology(net,agent,collector):
  print "*** Sending topology"
  topo = {'nodes':{}, 'links':{}}
  for s in net.switches:
    topo['nodes'][s.name] = {'agent':agent, 'ports':{}}
  path = '/sys/devices/virtual/net/'
  for child in listdir(path):
    parts = re.match('(^s[0-9]+)-(.*)', child)
    if parts == None: continue
    ifindex = open(path+child+'/ifindex').read().split('\n',1)[0]
    topo['nodes'][parts.group(1)]['ports'][child] = {'ifindex': ifindex}
  i = 0
  for s1 in net.switches:
    j = 0
    for s2 in net.switches:
      if j > i:
        intfs = s1.connectionsTo(s2)
        for intf in intfs:
          s1ifIdx = topo['nodes'][s1.name]['ports'][intf[0].name]['ifindex']
          s2ifIdx = topo['nodes'][s2.name]['ports'][intf[1].name]['ifindex']
          linkName = '%s-%s' % (s1.name, s2.name)
          topo['links'][linkName] = {'node1': s1.name, 'port1': intf[0].name, 'node2': s2.name, 'port2': intf[1].name}
      j += 1
    i += 1

  put('http://'+collector+':8008/topology/json',data=dumps(topo))

def wrapper(fn,collector):
  def result( *args, **kwargs):
    res = fn( *args, **kwargs)
    net = args[0]
    (ifname, agent) = getIfInfo(collector)
    configSFlow(net,collector,ifname)
    sendTopology(net,agent,collector) 
    return res
  return result

setattr(Mininet, 'start', wrapper(Mininet.__dict__['start'], collector))

