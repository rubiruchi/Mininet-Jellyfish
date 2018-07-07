Mininet: Rapid Prototyping for Software Defined Networks
========================================================
*The best way to emulate almost any network on your laptop!*

Mininet 2.3.0d1

[![Build Status][1]](https://travis-ci.org/mininet/mininet)

### run jellyfish topology in Mininet?

Mininet emulates a complete network of hosts, links, and switches
on a single machine.  To create a sample two-host, one-switch network,
just run:

  `sudo mn --custom sflow-jellyfish.py --topo jellyfish --controller=remote,ip=127.0.0.1,port=6653 --switch ovsk,protocols=OpenFlow13
`
