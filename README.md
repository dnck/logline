# Quick start

Ship your log lines via UDP packets to a server accepting log lines:

```
python3 ship_log.py -fname ~/logs/logFile.log -host ip.com -port 5222  
```
<hr>

Accept log lines from a shipper and print them to console.
```
python3 receive_log.py -host 192.168.2.69 -port 5222
```
<hr>
To receive log lines, if you are behind NAT, make sure you have port forwarding turned on and your firewall is accepting traffic on the port.

On Ubuntu, this can be configured by investigating ufw.

More robust architectures can be built on top of this pattern.
