#!/bin/bash

# get measurements of your internet connection with iperf3
# usage: netmeasure.sh OR netmeasure.sh <debug>

# bash strict mode
set -o errexit
set -o nounset
set -o pipefail
IFS=$'\n\t'

# set servers and ports
# list of public iperf servers from https://iperf.fr/iperf-servers.php
servers=("bouygues.iperf.fr"
	"ping.online.net"
	"iperf.eenet.ee"
	"iperf.volia.net"
	"iperf.it-north.net"
	"iperf.biznetnetworks.com"
	"iperf.scottlinux.com"
	"iperf.he.net"
)

ports="$(seq 5200 5209)"

function usage () {
	# usage: usage
	echo -e "Usage: ${0} OR ${0} debug"
}

function log () {
	# usage: log <message>
	local logdir="logs"
	local logfile="${logdir}/general.log"
	local timestamp="$(date +'%Y-%m-%d %H:%M')"

	if [ ! -e "${logdir}" ]; then
		mkdir -p "${logdir}"
	fi

	echo -e "${timestamp}: ${1}" >> "${logfile}"
}

function create_resultdir () {
	# usage: create_resultdir
	local resultdir="$(date +'%Y-%m-%d_%H-%M')"

	if [ ! -e "${resultdir}" ]; then
		mkdir -p "${resultdir}"
	fi

	echo "${resultdir}"

}

function run_test () {
	# usage: run_test <server> <port> <resultdir>
	local server="${1}"
	local port="${2}"
	local resultdir="${3}"

	local resultfile="${resultdir}/${server}_${port}.log"

	if [ -z ${DEBUG:-} ]; then
		iperf3	--logfile "${resultfile}" \
			--format m \
			--verbose \
			--json \
			--reverse \
			--port "${port}" \
			--client \
			"${server}" 2>&1 >/dev/null \
			|| {	rm "${resultfile}"; \
				return -1;
			}
	else
		log "Testing ${server}:${port}"
		echo "Testing ${server}:${port}"
		iperf3	--logfile "${resultfile}" \
			--format m \
			--verbose \
			--debug \
			--reverse \
			--port "${port}" \
			--client \
			"${server}" 2>&1 \
			|| {	log "${server}:${port} unreachable"; \
				rm "${resultfile}"; \
				return -1;
			} 
		log "Success"
	fi
}

# check if people are using this correctly
if [ "$#" -gt 1 ]; then
	usage
	exit -1
fi

# check if we are debugging
if [ ! -z ${1:-} ]; then
	DEBUG="debug"
fi

resultdir="$(create_resultdir)"

# iterate over each server and port from the list, if a server:port combination
# works, continue with the next server
for server in ${servers[@]}; do
	for port in ${ports[@]}; do
		run_test "${server}" "${port}" "${resultdir}"\
			&& continue 2 \
			|| continue
	done
done
