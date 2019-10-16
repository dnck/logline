# Quick start

Ship your log lines from a file via UDP packets to a server accepting log lines:
```
python3 ship_log.py -fname ~/logs/logFile.log -host ip.com -port 5222  
```

Ship your log lines from a pipe via UDP packets to a server accepting log lines. From the directory of your docker-compose.yml file,
```
docker-compose logs --no-color -f | python3 pipe_log.py -host ip.com -port 5222  
```

Note, after the above commands, you can add a ```&``` to run this in the background.

<hr>

Accept log lines from a shipper and print them to console.
```
python3 receive_log.py -host 192.168.2.69 -port 5222
```
<hr>
To receive log lines, if you are behind NAT, make sure you have port forwarding turned on and your firewall is accepting traffic on the port.

On Ubuntu, this can be configured by investigating ufw.

More robust architectures can be built on top of this pattern.


# Run docker_ship_log.py
```
docker build -f shipper.Dockerfile -t py_log_shipper .
docker run --name py_log_shipper -v LOG_DIRECTORY -d py_log_shipper
```
