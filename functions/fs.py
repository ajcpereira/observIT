import time
from functions.netcat import *
import re
import logging

def fs(hostname, ssh, PLATFORM, PLATFORM_NAME, type, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO):

        def cafs_iostat():
	#########################
	#CAFS_IOSTAT
	#########################
                log_stamp=time.time()
                logging.info("Starting metrics - %s" % log_stamp)
                #CMD1="/opt/fsc/CentricStor/bin/rdNsdInfos -a > /tmp/stats_nsd.out"
                #CMD2="iostat -x -k 1 2| awk '!/^sd/'|awk -vN=2 '/avg-cpu/{++n} n>=N' > /tmp/stats_iostat.out"
                CMD3="awk 'NR==FNR{a[$1]=$0; next} $3 in a{print a[$3],$0}' /tmp/stats_iostat.out /tmp/stats_nsd.out | awk '{print $18" "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "$10" "$11" "$12" "$13" "$14" "$15" "$16" "$17}' | sort"

                if PLATFORM_USE_SUDO == "yes":
                    CMD1 = "sudo " + CMD1
                    CMD2 = "sudo " + CMD2
                    CMD2 = "sudo " + CMD3

                #ssh.exec_command(CMD1)
                #ssh.exec_command(CMD2)
                stdin, stdout, stderr = ssh.exec_command(CMD3, get_pty=True)
                timestamp = int(time.time())
		
                #response = stdout.read().decode('ascii')
		
                response = stdout.read()
                response2 = stdout.read().decode('ascii')
                
                logging.info("SSH Output on function FS - %s" % response)
                logging.info("SSH Output on function FS decode - %s" % response2)
             
                for line in response.splitlines():
                    #if len(line.split())==16 and not line.startswith("\n") and not line.startswith("Device"):
                    logging.info("SSH Output on function FS response - %s" % line)
                    columns = line.split()
                    logging.info("SSH Output on function FS response columns - %s" % columns)
                    netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[17]) + "." + "svctm" + " " + re.sub(",",".",columns[15]) +" "+ str(timestamp) + "\n")
                    netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[17]) + "." + "%util" + " " + re.sub(",",".",columns[16]) +" "+ str(timestamp) + "\n")
                
                logging.info("Finished metrics - %s" % log_stamp)

        cafs_iostat()

#########################
#NEXT METRIC
