import time
from functions_core.netcat import *
from functions_core.secure_connect import *
import re, os, logging


def cs_iostat(**args):

    logging.info("Starting func_eternus_icp_fs")

    # Command line to run remotly
    CMD1="/opt/fsc/CentricStor/bin/rdNsdInfos -a > /tmp/stats_nsd.out"
    CMD2="/usr/bin/iostat -x -k 1 2| awk '!/^sd/'|awk -vN=2 '/avg-cpu/{++n} n>=N' > /tmp/stats_iostat.out"
    CMD3="awk \'NR==FNR{a[$1]=$0; next} $3 in a{print a[$3],$0}\' /tmp/stats_iostat.out /tmp/stats_nsd.out | awk '{print $18\" \"$1\" \"$2\" \"$3\" \"$4\" \"$5\" \"$6\" \"$7\" \"$8 \" \"$9\" \"$10\" \"$11\" \"$12\" \"$13\" \"$14\" \"$15\" \"$16\" \"$17}' | sort"
    
    logging.debug("Use_sudo is set to %s and ip_use_sudo %s" % (args['use_sudo'], args['ip_use_sudo']))
    
    if os.path.isfile("tests/cafs_iostat"):
          CMD1 = "cat tests/cafs_iostat"
          CMD2 = CMD1
          CMD3 = CMD1
          logging.info("cafs_iostat file exists, it will be used for tests")


    if args['use_sudo'] or args['ip_use_sudo']:
            CMD1 = "sudo " + CMD1
            logging.debug("Will use CMD1 with sudo - %s" % CMD1)
    
    logging.debug("Command Line 1 - %s" % CMD1)
    logging.debug("Command Line 2 - %s" % CMD2)
    logging.debug("Command Line 3 - %s" % CMD3)

    logging.info("Calling core function ssh")

    if args['ip_bastion']:
          bastion=args['ip_bastion']
    elif args['use_sudo']:
          bastion=args['bastion']
    else:
          bastion=None

    if args['ip_host_keys']:
          host_keys=args['ip_host_keys']
    elif args['host_keys']:
          host_keys=args['host_keys']
    else:
          host_keys=None

    try:
        ssh=Secure_Connect(args['ip'],bastion,args['user'],host_keys)
    except Exception as msgerror:
        logging.error("Failed to connect to %s" % args['ip'])
        return -1
    
    print("This is my session %s" % ssh)

    mycmd="echo Runned"
    myoutput=ssh.run(mycmd)
    print("Will print %s" % myoutput)
    
    ssh.ssh_run(CMD1)
    ssh.ssh_run(CMD2)
    stdout = ssh.ssh_run(CMD3, hide=True)
    timestamp = int(time.time())
    response = stdout.stdout
    logging.debug("Output of Command Line 3 - %s" % response)
    logging.info("Finished ssh execution to get metrics - %s" % time.ctime())
    for line in response.splitlines():
        if args['alias']:
              hostname = args['alias']
        else:
              hostname = hostname.replace(".","-dot-")
        if len(line.split())==18 and not line.startswith("\n") and not line.startswith("Device"):
            logging.info("Starting metrics processing on FS type - %s" % time.ctime())
            columns = line.split()
            netcat(args['repository'], args['repository_port'], args['repository_protocol'],  str(args['name']) + "." + str(type) + "." + hostname + "." + "fs" + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[17]) + "." + "svctm" + " " + re.sub(",",".",columns[15]) +" "+ str(timestamp) + "\n")
            netcat(args['repository'], args['repository_port'], args['repository_protocol'],  str(args['name']) + "." + str(type) + "." + hostname + "." + "fs" + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[17]) + "." + "%util" + " " + re.sub(",",".",columns[16]) +" "+ str(timestamp) + "\n")
            logging.info("Finished metrics processing on FS type - %s" % time.ctime())

    ssh.ssh_del()
            
    logging.info("Finished core function ssh with args %s" % args)

#    ssh.run(CMD1)
#    ssh.run(CMD2)
#    stdout = ssh.run(CMD3, hide=True)
#    timestamp = int(time.time())
#    response = stdout.stdout
#    logging.debug("Output of Command Line 3 - %s" % response)
#    logging.info("Finished ssh execution to get metrics - %s" % time.ctime())
#    for line in response.splitlines():
#        if len(line.split())==18 and not line.startswith("\n") and not line.startswith("Device"):
#            logging.info("Starting metrics processing on FS type - %s" % time.ctime())
#            columns = line.split()
#            netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + hostname.replace(".","-") + "." + "fs" + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[17]) + "." + "svctm" + " " + re.sub(",",".",columns[15]) +" "+ str(timestamp) + "\n")
#            netcat(PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL,  str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(type) + "." + hostname.replace(".","-") + "." + "fs" + str(columns[0]) + "." + str(columns[1]) + "." + str(columns[17]) + "." + "%util" + " " + re.sub(",",".",columns[16]) +" "+ str(timestamp) + "\n")
#            logging.info("Finished metrics processing on FS type - %s" % time.ctime())