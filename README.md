# netmeasure
Simple script to measure network throughput via iperf3

## Requirements
netmeasure.sh depends on bash and a working version of iperf3
netmeasureanalyzer.py depends on Python3 and matplotlib.

## Usage
Run ``netmeasure.sh debug`` to check if the script is working. Run
``netmeasure.sh`` in production use.

For best results it is advisable to add netmeasure.sh to your crontab and run it
in regular intervals over a longer time, e. g. every 4 hours for about 4 weeks.

After you have gathered at least two full runs of netmeasure.sh, you can then
use netmeasureanalyzer.py to plot the results.

## Internal workings
netmeasure.sh loops over two directions, up- and download, and inside the test
function iterates over the 8 public iperf-servers listed on [this iperf
website](https://iperf.fr/iperf-servers.php) that are reachable on a port
between 5200 and 5209. Inside the server list, the script loops over those
ports. As soon as a working connection can be made using iperf3, an iperf-run is
done to gather the transmission speed data.

If a connection cannot be made to a server-port-combination, the port is counted
up until 5209 is reached. If connection attempts fail for all ports, the next
server is tried. If a successful connection can be achieved, the loop also goes
to the next server.

As soon as all loops are ended, the script ends.

Then the output can be analyzed with netmeasureanalyzer.py which by default
plots the output and saves it to 'fig.png'.
