#!/bin/bash

# get measurements of your internet connection with iperf3
# usage: netmeasure.sh OR netmeasure.sh <debug>

# bash strict mode
set -o errexit
set -o nounset
set -o pipefail
IFS=$'\n\t'

# check if we are debugging
if [ -z "${1:-}" ]; then
	DEBUG=''
else
	DEBUG="debug"
fi

directions=("upload"
	"download"
)

function usage () {
	# usage: usage
	echo -e "Usage: ${0} OR ${0} debug"
}

function debug () {
	# usage: log <message>
	local logdir="logs"
	local logfile="${logdir}/general.log"
	local timestamp=""
	timestamp="$(date +'%Y-%m-%d %H:%M')"

	if [ ! -e "${logdir}" ]; then
		mkdir -p "${logdir}"
	fi

	logstring="${timestamp}: ${1}"

	if [ ! -z "${DEBUG}" ]; then
		printf '%s\n' "${logstring}" >> "${logfile}"
	fi

	printf '%s\n' "${logstring}"
}

function create_resultdir () {
	# usage: create_resultdir
	local resultdir=""
	resultdir="results/$(date +'%Y-%m-%d_%H-%M')"

	if [ ! -e "${resultdir}" ]; then
		mkdir -p "${resultdir}"
	fi

	echo "${resultdir}"

}

resultdir="$(create_resultdir)"

function run_test () {
	# usage: run_test <direction>
	local resultdir="${resultdir}"
	local direction="${1}"

	# set servers and ports
	# list of public iperf servers from https://iperf.fr/iperf-servers.php
	local servers=("bouygues.iperf.fr"
	"ping.online.net"
	"iperf.eenet.ee"
	"iperf.volia.net"
	"iperf.it-north.net"
	"iperf.biznetnetworks.com"
	"iperf.scottlinux.com"
	"iperf.he.net"
	)

	local ports=""
	ports="$(seq 5200 5209)"

	trap "rm -rf \"${resultdir}\"; debug 'Caught SIGINT'; exit 1" INT
	trap "rm -rf \"${resultdir}\"; debug 'Caught SIGTERM'; exit 1" TERM
	for server in "${servers[@]}"; do
		for port in "${ports[@]}"; do
			local resultfile="${resultdir}/${server}_${port}.${direction}"
			iperf_args=()
			if [ -z "${DEBUG}" ]; then
				iperf_args+=("--json")
			else
				iperf_args+=(	"--debug"
						"--format"
						"m"
				)
			fi
			if [ "${direction}" == "download" ]; then
				iperf_args+=("--reverse")
			fi
			iperf_args+=(	"--logfile"
					"${resultfile}"
					"--verbose"
					"--port"
					"${port}"
					"--client"
					"${server}"
			)
			if [ -z "${DEBUG}" ]; then
				iperf_args+=("2>&1 >/dev/null")
			fi

			debug "Testing ${direction} ${server}:${port}";
			iperf3 "${iperf_args[@]}" \
			|| {	rm "${resultfile}"; \
				debug "${direction} ${server}:${port} failed";\
				continue;
			}\
			&& continue 2
		done
	done
	trap - INT TERM
}

# check if people are using this correctly
if [ "$#" -gt 1 ]; then
	usage
	exit -1
fi

# iterate over each server and port from the list, if a server:port combination
# works, continue with the next server
for direction in "${directions[@]}"; do
	run_test "${direction}"
done
