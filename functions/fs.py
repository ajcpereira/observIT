import time
from functions.netcat import *
import re
import logging


def fs(hostname, ssh, PLATFORM, PLATFORM_NAME, type, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO):

        def cafs_iostat():
	    #########################
	    #CAFS_IOSTAT
	    #########################
                logging.info("Starting ssh execution to get metrics - %s" % time.ctime())
                CMD1="/opt/fsc/CentricStor/bin/rdNsdInfos -a > /tmp/stats_nsd.out"
                CMD2="iostat -x -k 1 2| awk '!/^sd/'|awk -vN=2 '/avg-cpu/{++n} n>=N' > /tmp/stats_iostat.out"
                CMD3="awk \'NR==FNR{a[$1]=$0; next} $3 in a{print a[$3],$0}\' /tmp/stats_iostat.out /tmp/stats_nsd.out | awk '{print $18\" \"$1\" \"$2\" \"$3\" \"$4\" \"$5\" \"$6\" \"$7\" \"$8 \" \"$9\" \"$10\" \"$11\" \"$12\" \"$13\" \"$14\" \"$15\" \"$16\" \"$17}' | sort"
                
                if PLATFORM_USE_SUDO == "yes":
                    CMD1 = "sudo " + CMD1
                    logging.debug("Will use CMD1 with sudo - %s" % CMD1)

                logging.debug("Command Line 1 - %s" % CMD1)
                logging.debug("Command Line 2 - %s" % CMD2)
                logging.debug("Command Line 3 - %s" % CMD3)

                ssh.run(CMD1)
                ssh.run(CMD2)

                stdout = ssh.run(CMD3, hide=True)
                timestamp = int(time.ctime())

                response = stdout.stdout

                logging.debug("Output of Command Line 3 - %s" % response)
                logging.info("Finished ssh execution to get metrics - %s" % time.ctime())
             
                for line in response.splitlines():
                    if len(line.split())==18 and not line.startswith("\n") and not line.startswith("Device"):
                        logging.info("Starting metrics processing on FS type - %s" % time.ctime())
                        columns = line.split()
                        netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + hostname.replace(".","-") + "." + "fs" + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[17]) + "." + "svctm" + " " + re.sub(",",".",columns[15]) +" "+ str(timestamp) + "\n")
                        netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + hostname.replace(".","-") + "." + "fs" + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[17]) + "." + "%util" + " " + re.sub(",",".",columns[16]) +" "+ str(timestamp) + "\n")
                        logging.info("Finished metrics processing on FS type - %s" % time.ctime())

        ########################## 
        ##NEXT METRIC
        ##########################

        ########################## 
        ##EXECUTE SUB-FUNCTIONS
        ##########################
        cafs_iostat()


