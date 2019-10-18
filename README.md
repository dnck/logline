# Logline
Logline tails your log file, and streams them via UDP to a centralized log server. It is built for the Helix Network's pendulum package.

# Features
- [x] A two-threaded log-shipper that sends new lines from your .log file to a server
- [x] A simple centralized UDP server that receives log lines and writes them them to a final file.
- [x] Toleration for changes in log file, in case you restart your node, or the log file rolls over and changes name.
- [x] Notifications in telegram of initialization and any changes in log shipping.
- [x] An additional submodule specific to the Helix pendulum node that scraps the log file and sends metrics to a Prometheus endpoint.


# Quick start

Ship your log lines from a file via UDP packets to a server accepting log lines:
```
python3 ship_log.py /home/ubuntu/data/logs -host send.here.net -port 5222 -node_name relayer1 &
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
This is a work in progress. Here's a list of TODOs to get this feature working:

* The ship_log.py script should accept four arguments. These arguments need to be passed to ```docker run```, or they need to be within the environment, and then the shipper needs to get these from a ```os.environ.get("KEY")``` call.

Here's a helpful stackoverflow response on the question,
https://stackoverflow.com/questions/46245844/pass-arguments-to-python-argparse-within-docker-container/46246032

Here's how the building and running should look, at minimum:

```
docker build -f shipper.Dockerfile -t py_log_shipper .
docker run --name py_log_shipper -v LOG_DIRECTORY:LOG_DIRECTORY -d py_log_shipper
```
