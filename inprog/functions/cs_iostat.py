from functions_core.netcat import *
from functions_core.secure_connect import *
import re, os, logging, subprocess, time


def cs_iostat(**args):

    logging.debug("Starting func_eternus_icp_fs")

    # Command line to run remotly
    cmd1="/opt/fsc/CentricStor/bin/rdNsdInfos -a > /tmp/stats_nsd.out"
    cmd2="/usr/bin/iostat -x -k 1 2| awk '!/^sd/'|awk -vN=2 '/avg-cpu/{++n} n>=N' > /tmp/stats_iostat.out"
    cmd3="awk \'NR==FNR{a[$1]=$0; next} $3 in a{print a[$3],$0}\' /tmp/stats_iostat.out /tmp/stats_nsd.out | awk '{print $18\" \"$1\" \"$2\" \"$3\" \"$4\" \"$5\" \"$6\" \"$7\" \"$8 \" \"$9\" \"$10\" \"$11\" \"$12\" \"$13\" \"$14\" \"$15\" \"$16\" \"$17}' | sort"
    
    logging.debug("Use_sudo is set to %s and ip_use_sudo %s" % (args['use_sudo'], args['ip_use_sudo']))
    
    if os.path.isfile("tests/cafs_iostat"):
          logging.info("cafs_iostat file exists, it will be used for tests")
          flag_test=True
          cmd1 = "echo TEST"
          cmd2 = cmd1
          cmd3 = subprocess.run(['cat', './tests/cafs_iostat'], stdout=subprocess.PIPE).stdout.decode('utf-8')
          logging.debug("cmd3 for test %s" % cmd3)
          

    if args['use_sudo'] or args['ip_use_sudo']:
            cmd1 = "sudo " + cmd1
            logging.debug("Will use cmd1 with sudo - %s" % cmd1)
    
    logging.debug("Command Line 1 - %s" % cmd1)
    logging.debug("Command Line 2 - %s" % cmd2)
    logging.debug("Command Line 3 - %s" % cmd3)

    if args['ip_bastion']:
          bastion=str(args['ip_bastion'])
    elif args['use_sudo']:
          bastion=str(args['bastion'])
    else:
          bastion=None

    if args['ip_host_keys']:
          host_keys=args['ip_host_keys']
    elif args['host_keys']:
          host_keys=args['host_keys']
    else:
          host_keys=None

    try:
        ssh=Secure_Connect(str(args['ip']),bastion,args['user'],host_keys)
    except Exception as msgerror:
        logging.error("Failed to connect to %s" % args['ip'])
        return -1
    
    logging.debug("This is my ssh session from the Class Secure_Connect %s" % ssh)
    
    NONE = ssh.ssh_run(cmd1)
    NONE = ssh.ssh_run(cmd2)

    if flag_test:
         response = cmd3
    else:
         stdout = ssh.ssh_run(cmd3)
         response = stdout.stdout
    timestamp = int(time.time())
    
    logging.debug("Output of Command Line 3 - %s" % response)
    
    for line in response.splitlines():
        if args['alias']:
              hostname = args['alias']
        else:
              hostname = str(args['ip']).replace(".","-dot-")
        if len(line.split())==18 and not line.startswith("\n") and not line.startswith("Device"):
            logging.debug("Starting metrics processing on FS type - %s" % time.ctime())
            
            columns = line.split()
            netcat(args['repository'], args['repository_port'], args['repository_protocol'],  str(args['name']) + "." + str(args['resources_types']) + "." + hostname + "." + "fs" + "." + str(columns[16]) + "." + str(columns[0]) + "." + str(columns[17]) + "." + "svctm" + " " + re.sub(",",".",columns[14]) +" "+ str(timestamp) + "\n")
            netcat(args['repository'], args['repository_port'], args['repository_protocol'],  str(args['name']) + "." + str(args['resources_types']) + "." + hostname + "." + "fs" + "." + str(columns[16]) + "." + str(columns[0]) + "." + str(columns[17]) + "." + "r_await" + " " + re.sub(",",".",columns[9]) +" "+ str(timestamp) + "\n")
            netcat(args['repository'], args['repository_port'], args['repository_protocol'],  str(args['name']) + "." + str(args['resources_types']) + "." + hostname + "." + "fs" + "." + str(columns[16]) + "." + str(columns[0]) + "." + str(columns[17]) + "." + "w_await" + " " + re.sub(",",".",columns[10]) +" "+ str(timestamp) + "\n")
            logging.debug("Finished metrics processing on FS type - %s" % time.ctime())

    ssh.ssh_del()
            
    logging.debug("Finished core function ssh with args %s" % args)