import time
from functions.netcat import *
import re
import logging

my_threads = ['cafs_iostat']

def fs(hostname, ssh, PLATFORM, PLATFORM_NAME, type, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO):

	def cafs_iostat():
	#########################
	#CAFS_IOSTAT
	#########################
		log_stamp=time.time()
		logging.info("Starting metrics - %s" % log_stamp)
		CMD1="iostat -x 1 2"

		if PLATFORM_USE_SUDO == "yes":
			CMD1 = "sudo " + CMD1

		stdin, stdout, stderr = ssh.exec_command(CMD1)
		timestamp = int(time.time())

		header=1
		response = stdout.read().decode('ascii')

		for line in response.splitlines():
			if line.startswith("Device"):
				header +=1
				columns = line.split()
				legend_metric_a=columns[5]
				legend_metric_b=columns[11]
			if len(line.split())==21 and not line.startswith("\n") and header == 2 and not line.startswith("Device"):
				columns = line.split()
				netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + re.sub("\.","-", hostname) + "." + str(columns[0]) + "." + str(legend_metric_a) + " " + re.sub(",",".",columns[5]) +" "+ str(timestamp) + "\n")
				netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + re.sub("\.","-", hostname) + "." + str(columns[0]) + "." + str(legend_metric_b) + " " + re.sub(",",".",columns[11]) +" "+ str(timestamp) + "\n")

		logging.info("Finished metrics - %s" % log_stamp)

	cafs_iostat()
		

#	ssh.exec_command("/opt/fsc/CentricStor/bin/rdNsdInfos -a > /tmp/stats_nsd.out")
#	ssh.exec_command("iostat -x -k 1 2| awk '!/^sd/'|awk -vN=2 '/avg-cpu/{++n} n>=N' > /tmp/stats_iostat.out")
#	stdin, stdout, stderr = ssh.exec_command("awk 'NR==FNR{a[$1]=$0; next} $3 in a{print a[$3],$0}' /tmp/stats_iostat.out /tmp/stats_nsd.out | awk '{print $18" "$1" "$2" "$3" "$4" "$5" "$6" "$78" "$9" "$10" "$11" "$12" "$13" "$14" "$15" "$16" "$17}' | sort")
#
#	timestamp = int(time.time())
#	response = stdout.read().decode('ascii')
#
#	for line in response.splitlines():
#		if len(line.split())==16 and not line.startswith("\n") and not line.startswith("Device"):
#			columns = line.split()
#						
#			netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[16]) + "." + "svctm" + " " + re.sub(",",".",columns[14]) +" "+ str(timestamp) + "\n")
#			netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[16]) + "." + "%util" + " " + re.sub(",",".",columns[15]) +" "+ str(timestamp) + "\n")		



#########################
#NEXT METRIC
#########################