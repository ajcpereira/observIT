import os, logging, subprocess, time
from functions_core.send_influxdb import *
from functions_core.secure_connect import *


def eternus_cs8000_fs_io(**args):

    logging.debug("Starting func_eternus_cs8000_fs_io")

    # Command line to run remotly
    cmd1="/opt/fsc/CentricStor/bin/rdNsdInfos -a > /tmp/stats_nsd.out"
    cmd2="/usr/bin/iostat -x -k 1 2| awk '!/^sd/'|awk -vN=2 '/avg-cpu/{++n} n>=N' > /tmp/stats_iostat.out"
    cmd3="awk \'NR==FNR{a[$1]=$0; next} $3 in a{print a[$3],$0}\' /tmp/stats_iostat.out /tmp/stats_nsd.out | awk '{print $18\" \"$1\" \"$2\" \"$3\" \"$4\" \"$5\" \"$6\" \"$7\" \"$8 \" \"$9\" \"$10\" \"$11\" \"$12\" \"$13\" \"$14\" \"$15\" \"$16\" \"$17}' | sort"
    
    logging.debug("Use_sudo is set to %s and ip_use_sudo %s" % (args['use_sudo'], args['ip_use_sudo']))

    if args['use_sudo'] or args['ip_use_sudo']:
            cmd1 = "sudo " + cmd1
            logging.debug("Will use cmd1 with sudo - %s" % cmd1)

    flag_test=None
    
    if os.path.isfile("tests/cafs_iostat"):
          logging.info("cafs_iostat file exists, it will be used for tests")
          flag_test=True
          cmd1 = "echo TEST"
          cmd2 = cmd1
          cmd3 = subprocess.run(['cat', './tests/cafs_iostat'], stdout=subprocess.PIPE).stdout.decode('utf-8')
          logging.debug("cmd3 for test %s" % cmd3)
          logging.warning("You are using test file for FS_IO, not really data")
          
    logging.debug("Command Line 1 - %s" % cmd1)
    logging.debug("Command Line 2 - %s" % cmd2)
    logging.debug("Command Line 3 - %s" % cmd3)

    if args['ip_bastion']:
          bastion=str(args['ip_bastion'])
    elif args['bastion']:
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
    
    record = []

    logging.debug("Starting metrics processing on FS_IO")

    for line in response.splitlines():
        if args['alias']:
              hostname = args['alias']
        else:
              hostname = str(args['ip'])

        if len(line.split()) == 18 and not line.startswith("\n") and not line.startswith("Device"):
            
            columns = line.split()

            record = record + [
                     {"measurement": "fs_io",
                              "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname,
                                       "fs": str(columns[0]), "dm": str(columns[1]),"rawdev": str(columns[17])},
                              "fields": {"svctm": float(columns[15]), "r_await": float(columns[10]), "w_await": float(columns[11]), "r/s": float(columns[2]), "w/s": float(columns[3])},
                              "time": timestamp
                              }
                         ]


    # Close ssh session
    ssh.ssh_del()
    logging.debug("Finished core function ssh with args %s" % args)
    
    # Send Data to InfluxDB
    logging.debug("Data to be sent to DB by FS_IO %s" % record)
    send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
            
    logging.debug("Finished core function ssh with args %s" % args)

def eternus_cs8000_drives(**args):

    logging.debug("Starting func_eternus_cs8000_drives")

    # Command line to run remotly
    cmd1="/opt/fsc/bin/plmcmd query -D"
    
    logging.debug("Use_sudo is set to %s and ip_use_sudo %s" % (args['use_sudo'], args['ip_use_sudo']))

    if args['use_sudo'] or args['ip_use_sudo']:
            cmd1 = "sudo " + cmd1
            logging.debug("Will use cmd1 with sudo - %s" % cmd1)
    
    logging.debug("Command Line 1 - %s" % cmd1)


    flag_test=None
    
    if os.path.isfile("tests/plmcmd_query-D"):
          logging.info("plmcmd_query-D file exists, it will be used for tests")
          flag_test=True
          cmd1 = subprocess.run(['cat', './tests/plmcmd_query-D'], stdout=subprocess.PIPE).stdout.decode('utf-8')
          logging.debug("cmd1 for test %s" % cmd1)
          logging.warning("You are using test file for Drives, not really data")
          

    ###########################################
    if args['ip_bastion']:
          bastion=str(args['ip_bastion'])
    elif args['bastion']:
          bastion=str(args['bastion'])
    else:
          bastion=None

    if args['ip_host_keys']:
          host_keys=args['ip_host_keys']
    elif args['host_keys']:
          host_keys=args['host_keys']
    else:
          host_keys=None

    if args['alias']:
        hostname = args['alias']
    else:
        hostname = str(args['ip'])
    ###########################################

    try:
        ssh=Secure_Connect(str(args['ip']),bastion,args['user'],host_keys)
    except Exception as msgerror:
        logging.error("Failed to connect to %s with error %s" % (args['ip'], msgerror))
        return -1
    
    logging.debug("This is my ssh session from the Class Secure_Connect %s" % ssh)
    
    if flag_test:
         response = cmd1
    else:
         stdout = ssh.ssh_run(cmd1)
         response = stdout.stdout

    timestamp = int(time.time())
    
    logging.debug("Output of Command Line 1 - %s" % response)
    
    logging.debug("Starting metrics processing on DRIVES")

    tapename = None
    count_unused = 0
    count_used = 0
    count_another_state = 0
    record=[]
    
    for line in response.splitlines():
        columns = line.split()
    
        if line.startswith("Tapelibrary"):    
            if tapename != None:
          
                record = record + [{"measurement": "drives", "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname, "tapename": tapename },
                                  "fields": {"total": int(count_used+count_unused+count_another_state), "used": int(count_used), "other": int(count_another_state)},
                                  "time": timestamp}]
    
                logging.debug("tapename %s total drives %s used %s unused %s other %s" % (tapename, count_used+count_unused+count_another_state, count_used, count_unused, count_another_state))
                count_unused = 0
                count_used = 0
                count_another_state = 0
                tapename = str(columns[1])
            else:
                tapename = str(columns[1])
        elif not columns[0].isdigit():
        #elif line.startswith("PLS") or line.startswith("pos"):
            continue
        else:
            if str(columns[2]) == "unused":
                count_unused = count_unused + 1
            elif str(columns[2]) == "occupied":
                count_used = count_used + 1
            else:
                count_another_state = count_another_state + 1
    
    record = record + [{"measurement": "drives", "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname, "tapename": tapename },
                                  "fields": {"total": int(count_used+count_unused+count_another_state), "used": int(count_used), "other": int(count_another_state)},
                                  "time": timestamp}]

    # Close ssh session
    ssh.ssh_del()        
    logging.debug("Finished core function ssh with args %s" % args)

    # Send Data to InfluxDB
    logging.debug("Data to be sent to DB by drives %s" % record)
    send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    
    logging.debug("Finished func_eternus_cs8000_drives ")

def eternus_cs8000_medias(**args):

    logging.debug("Starting func_eternus_cs8000_medias")

    # Command line to run remotly
    cmd1="/opt/fsc/bin/plmcmd query -V"
    
    logging.debug("Use_sudo is set to %s and ip_use_sudo %s" % (args['use_sudo'], args['ip_use_sudo']))

    if args['use_sudo'] or args['ip_use_sudo']:
            cmd1 = "sudo " + cmd1
            logging.debug("Will use cmd1 with sudo - %s" % cmd1)
    
    logging.debug("Command Line 1 - %s" % cmd1)


    flag_test=None
    
    if os.path.isfile("tests/plmcmd_query-V"):
          logging.info("plmcmd_query-V file exists, it will be used for tests")
          flag_test=True
          cmd1 = subprocess.run(['cat', './tests/plmcmd_query-V'], stdout=subprocess.PIPE).stdout.decode('utf-8')
          logging.debug("cmd1 for test %s" % cmd1)
          logging.warning("You are using test file for Drives, not really data")
          

    ###########################################
    if args['ip_bastion']:
          bastion=str(args['ip_bastion'])
    elif args['bastion']:
          bastion=str(args['bastion'])
    else:
          bastion=None

    if args['ip_host_keys']:
          host_keys=args['ip_host_keys']
    elif args['host_keys']:
          host_keys=args['host_keys']
    else:
          host_keys=None

    if args['alias']:
        hostname = args['alias']
    else:
        hostname = str(args['ip'])
    ###########################################

    try:
        ssh=Secure_Connect(str(args['ip']),bastion,args['user'],host_keys)
    except Exception as msgerror:
        logging.error("Failed to connect to %s with error %s" % (args['ip'], msgerror))
        return -1
    
    logging.debug("This is my ssh session from the Class Secure_Connect %s" % ssh)
    
    if flag_test:
         response = cmd1
    else:
         stdout = ssh.ssh_run(cmd1)
         response = stdout.stdout

    timestamp = int(time.time())
    
    logging.debug("Output of Command Line 1 - %s" % response)
    
    logging.debug("Starting metrics processing on MEDIAS")


    ##############################
    library = {}
    record = []
    
    for line in response.splitlines():
        columns = line.split()
        if line.__contains__("pos"):
            continue
        else:
            # Library Libname / Count Medias / Total Cap / Total Valid / Val% / Clean / Inacessible / Fault
            # PVG_Library PVG / Total PV's / Fault / Ina / Scr / -10 / -20 / -30 / -40 / -50 / -60 / -70 / -80 / -90 / >90 / Total Cap TB / Use Cap TB
            # Scratch if fill_grade == 0 and $5 == o___
            if str(columns[2]) not in library.keys():
                if str(columns[4][0]) == 'i' and not str(columns[1]).startswith("CLN"):
                    library[str(columns[2])]=[str(columns[2]),0,0,0,0.0,0,1,0]
                elif str(columns[4][0]) == 'f' and not str(columns[1]).startswith("CLN"):
                    library[str(columns[2])]=[str(columns[2]),0,0,0,0.0,0,0,1]
                elif str(columns[1]).startswith("CLN"):
                    library[str(columns[2])]=[str(columns[2]),0,float(columns[8]),float(columns[9]),0.0,1,0,0]
                elif float(columns[8]) > 0.0 and not str(columns[1]).startswith("CLN"):
                    library[str(columns[2])]=[str(columns[2]),1,float(columns[8]),float(columns[9]),float(columns[10]),0,0,0]
                else:
                    logging.error("This line requires development analysis -  %s" % columns)
            else:
                if str(columns[4][0]) == 'i' and not str(columns[1]).startswith("CLN"):
                    library[str(columns[2])]=[str(columns[2]),int(library[str(columns[2])][1])+0,float(library[str(columns[2])][2]),float(library[str(columns[2])][3]),float(library[str(columns[2])][4]),int(library[str(columns[2])][5])+0,int(library[str(columns[2])][6])+1,int(library[str(columns[2])][7])+0]
                elif str(columns[4][0]) == 'f' and not str(columns[1]).startswith("CLN"):
                    library[str(columns[2])]=[str(columns[2]),int(library[str(columns[2])][1])+0,float(library[str(columns[2])][2]),float(library[str(columns[2])][3]),float(library[str(columns[2])][4]),int(library[str(columns[2])][5])+0,int(library[str(columns[2])][6])+0,int(library[str(columns[2])][7])+1]
                elif str(columns[1]).startswith("CLN"):
                    library[str(columns[2])]=[str(columns[2]),int(library[str(columns[2])][1])+0,float(library[str(columns[2])][2]),float(library[str(columns[2])][3]),float(library[str(columns[2])][4]),int(library[str(columns[2])][5])+1,int(library[str(columns[2])][6])+0,int(library[str(columns[2])][7])+0]
                elif float(columns[8]) > 0 and not str(columns[1]).startswith("CLN"):
                    library[str(columns[2])]=[str(columns[2]),int(library[str(columns[2])][1])+1,float(library[str(columns[2])][2])+float(columns[8]),float(library[str(columns[2])][3])+float(columns[9]),float(library[str(columns[2])][4])+float(columns[10]),int(library[str(columns[2])][5])+0,int(library[str(columns[2])][6])+0,int(library[str(columns[2])][7])+0]
                else:
                    logging.error("This line requires development analysis -  %s" % columns)

    for line in library.values():
        if line[4] != 0 and line[1] != 0:
            line[4]=line[4]/line[1]

        record = record + [{"measurement": "medias", "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname, "tapename": line[0] },
                                  "fields": {"Total Medias": line[1], "Total Cap GiB": line[2], "Total Val GiB": line[3], "Val %": line[4], "Total Clean Medias": line[5], "Total Ina": line[6], "Total Fault": line[7]},
                                  "time": timestamp}]
    ########################

    # Close ssh session
    ssh.ssh_del()        
    logging.debug("Finished core function ssh with args %s" % args)

    # Send Data to InfluxDB
    logging.debug("Data to be sent to DB by medias %s" % record)
    send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    
    logging.debug("Finished func_eternus_cs8000_medias")

def eternus_cs8000_pvgprofile(**args):

    logging.debug("Starting func_eternus_cs8000_pvgprofile")

    # Command line to run remotly
    cmd1="/opt/fsc/bin/plmcmd query -V | grep -v CLN | grep -v \'PVG\'"
    
    logging.debug("Use_sudo is set to %s and ip_use_sudo %s" % (args['use_sudo'], args['ip_use_sudo']))

    if args['use_sudo'] or args['ip_use_sudo']:
            cmd1 = "sudo " + cmd1
            logging.debug("Will use cmd1 with sudo - %s" % cmd1)
    
    logging.debug("Command Line 1 - %s" % cmd1)

    flag_test=None
    
    if os.path.isfile("./tests/plmcmd_pvgprofile"):
          logging.info("plmcmd_pvgprofile file exists, it will be used for tests")
          flag_test=True
          cmd="cat ./tests/plmcmd_pvgprofile | grep -v \'CLN\' | grep -v \'PVG\'"
          cmd1 = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
          logging.debug("cmd1 for test %s" % cmd1)
          logging.warning("You are using test file for PVG Profile, not really data")
          

    ###########################################
    if args['ip_bastion']:
          bastion=str(args['ip_bastion'])
    elif args['bastion']:
          bastion=str(args['bastion'])
    else:
          bastion=None

    if args['ip_host_keys']:
          host_keys=args['ip_host_keys']
    elif args['host_keys']:
          host_keys=args['host_keys']
    else:
          host_keys=None

    if args['alias']:
        hostname = args['alias']
    else:
        hostname = str(args['ip'])
    ###########################################

    try:
        ssh=Secure_Connect(str(args['ip']),bastion,args['user'],host_keys)
    except Exception as msgerror:
        logging.error("Failed to connect to %s with error %s" % (args['ip'], msgerror))
        return -1
    
    logging.debug("This is my ssh session from the Class Secure_Connect %s" % ssh)
    
    if flag_test:
         response = cmd1
    else:
         stdout = ssh.ssh_run(cmd1)
         response = stdout.stdout

    timestamp = int(time.time())
    
    logging.debug("Output of Command Line 1 - %s" % response)
    
    logging.debug("Starting metrics processing on PVGProfile")


    ##############################
    library = {}
    record = []

    for line in response.splitlines():
        columns = line.split()
        if line.__contains__("PVG"):
            continue
        else:
            if str(columns[3]) not in library.keys():
                if str(columns[4][0]) == 'f':
                    library[str(columns[3])]=[str(columns[3]),1,1,0,0,0,0,0,0,0,0,0,0,0,0,0.0,0.0]
                elif str(columns[4][0]) == 'i':
                    library[str(columns[3])]=[str(columns[3]),1,0,1,0,0,0,0,0,0,0,0,0,0,0,0.0,0.0]
                elif float(columns[10]) == 0 and str(columns[4][0]) == 'o':
                    library[str(columns[3])]=[str(columns[3]),1,0,0,1,0,0,0,0,0,0,0,0,0,0,float(columns[8]),float(columns[9])]
                elif float(columns[10]) >= 0:
                    if float(columns[10]) < 10:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,1,0,0,0,0,0,0,0,0,0,float(columns[8]),float(columns[9])]
                    elif float(columns[10]) >= 10 and float(columns[10]) < 20:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,0,1,0,0,0,0,0,0,0,0,float(columns[8]),float(columns[9])]
                    elif float(columns[10]) >= 20 and float(columns[10]) < 30:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,0,0,1,0,0,0,0,0,0,0,float(columns[8]),float(columns[9])]
                    elif float(columns[10]) >= 30 and float(columns[10]) < 40:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,0,0,0,1,0,0,0,0,0,0,float(columns[8]),float(columns[9])]
                    elif float(columns[10]) >= 40 and float(columns[10]) < 50:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,0,0,0,0,1,0,0,0,0,0,float(columns[8]),float(columns[9])]
                    elif float(columns[10]) >= 50 and float(columns[10]) < 60:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,0,0,0,0,0,1,0,0,0,0,float(columns[8]),float(columns[9])]
                    elif float(columns[10]) >= 60 and float(columns[10]) < 70:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,0,0,0,0,0,0,1,0,0,0,float(columns[8]),float(columns[9])]
                    elif float(columns[10]) >= 70 and float(columns[10]) < 80:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,0,0,0,0,0,0,0,1,0,0,float(columns[8]),float(columns[9])]
                    elif float(columns[10]) >= 80 and float(columns[10]) < 90:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,0,0,0,0,0,0,0,0,1,0,float(columns[8]),float(columns[9])]
                    elif float(columns[10]) >= 90:
                        library[str(columns[3])]=[str(columns[3]),1,0,0,0,0,0,0,0,0,0,0,0,0,1,float(columns[8]),float(columns[9])]
                    else:
                        logging.error("This line requires development analysis -  %s" % columns)
                else:
                    logging.error("This line requires development analysis -  %s" % columns)
            # PVG_Library PVG / Total PV's / Fault / Ina / Scr / -10 / -20 / -30 / -40 / -50 / -60 / -70 / -80 / -90 / >90 / Total Cap TB / Use Cap TB
            else:
                #                            tapename 0       Total PVG 1                           Fault 2                              Ina 3                            Scr 4                                -10 5                                -20 6                               -30 7                                -40 8                            -50 9                                -60 10                                -70 11                                -80 12                                -90 13                                +90 14                                Total Cap 15        Used Cap 16
                #library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3][1])])+0,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+0,float(library[str(columns[3])][16])+0]
                if str(columns[4][0]) == 'f':
                    library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+1,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+0,float(library[str(columns[3])][16])+0]
                elif str(columns[4][0]) == 'i':
                    library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+1,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+0,float(library[str(columns[3])][16])+0]
                elif float(columns[10]) == 0 and str(columns[4][0]) == 'o':
                    library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+1,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                elif float(columns[10]) >= 0:
                    if float(columns[10]) < 10:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+1,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    elif float(columns[10]) >= 10 and float(columns[10]) < 20:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+1,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    elif float(columns[10]) >= 20 and float(columns[10]) < 30:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+1,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    elif float(columns[10]) >= 30 and float(columns[10]) < 40:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+1,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    elif float(columns[10]) >= 40 and float(columns[10]) < 50:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+1,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    elif float(columns[10]) >= 50 and float(columns[10]) < 60:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+1,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    elif float(columns[10]) >= 60 and float(columns[10]) < 70:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+1,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    elif float(columns[10]) >= 70 and float(columns[10]) < 80:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+1,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    elif float(columns[10]) >= 80 and float(columns[10]) < 90:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+1,int(library[str(columns[3])][14])+0,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    elif float(columns[10]) >= 90:
                        library[str(columns[3])]=[str(columns[3]),int(library[str(columns[3])][1])+1,int(library[str(columns[3])][2])+0,int(library[str(columns[3])][3])+0,int(library[str(columns[3])][4])+0,int(library[str(columns[3])][5])+0,int(library[str(columns[3])][6])+0,int(library[str(columns[3])][7])+0,int(library[str(columns[3])][8])+0,int(library[str(columns[3])][9])+0,int(library[str(columns[3])][10])+0,int(library[str(columns[3])][11])+0,int(library[str(columns[3])][12])+0,int(library[str(columns[3])][13])+0,int(library[str(columns[3])][14])+1,float(library[str(columns[3])][15])+float(columns[8]),float(library[str(columns[3])][16])+float(columns[9])]
                    else:
                        logging.error("This line requires development analysis -  %s" % columns)
                else:
                    logging.error("This line requires development analysis -  %s" % columns)

    for line in library.values():
        # PVG_Library PVG / Total PV's / Fault / Ina / Scr / -10 / -20 / -30 / -40 / -50 / -60 / -70 / -80 / -90 / >90 / Total Cap TB / Use Cap TB
        record = record + [{"measurement": "pvgprofile", "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname, "pvgname": line[0] },
                                  "fields": {"Total Medias": line[1], "Fault": line[2], "Ina": line[3], "Scr": line[4], "-10": line[5], "-20": line[6], "-30": line[7], "-40": line[8], "-50": line[9], "-60": line[10], "-70": line[11], "-80": line[12], "-90": line[13], ">90": line[14], "Total Cap (GiB)": line[15], "Total Used (GiB)": line[16]},
                                  "time": timestamp}]
    ########################

    # Close ssh session
    ssh.ssh_del()
    logging.debug("Finished core function ssh with args %s" % args)

    # Send Data to InfluxDB
    logging.debug("Data to be sent to DB by pvgprofile %s" % record)
    send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    
    logging.debug("Finished func_eternus_cs8000_pvgprofile")
    
def eternus_cs8000_fc(**args):

    logging.debug("Starting func_eternus_cs8000_fc")

    # Command line to run remotly
    cmd1="for i in `ls /sys/class/fc_host`; do tx=`cat /sys/class/fc_host/$i/statistics/tx_words`; rx=`cat /sys/class/fc_host/$i/statistics/rx_words`; echo $i $tx $rx; done"
    
    logging.debug("Use_sudo is set to %s and ip_use_sudo %s" % (args['use_sudo'], args['ip_use_sudo']))

    #if args['use_sudo'] or args['ip_use_sudo']:
    #        cmd1 = "sudo " + cmd1
    #        logging.debug("Will use cmd1 with sudo - %s" % cmd1)
    
    logging.debug("Command Line 1 - %s" % cmd1)

    flag_test=None
    
    if os.path.isfile("./tests/fc_transmit"):
          logging.info("fc_transmit file exists, it will be used for tests")
          flag_test=True
          cmd="cat ./tests/fc_transmit"
          cmd1 = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
          logging.debug("cmd1 for test %s" % cmd1)
          logging.warning("You are using test file for FC, not really data")
          

    ###########################################
    if args['ip_bastion']:
          bastion=str(args['ip_bastion'])
    elif args['bastion']:
          bastion=str(args['bastion'])
    else:
          bastion=None

    if args['ip_host_keys']:
          host_keys=args['ip_host_keys']
    elif args['host_keys']:
          host_keys=args['host_keys']
    else:
          host_keys=None

    if args['alias']:
        hostname = args['alias']
    else:
        hostname = str(args['ip'])
    ###########################################

    try:
        ssh=Secure_Connect(str(args['ip']),bastion,args['user'],host_keys)
    except Exception as msgerror:
        logging.error("Failed to connect to %s with error %s" % (args['ip'], msgerror))
        return -1
    
    logging.debug("This is my ssh session from the Class Secure_Connect %s" % ssh)
    
    if flag_test:
         response = cmd1
    else:
         stdout = ssh.ssh_run(cmd1)
         response = stdout.stdout

    timestamp = int(time.time())
    
    logging.debug("Output of Command Line 1 - %s" % response)
    
    logging.debug("Starting metrics processing on FC")


    ##############################
    record = []
    for line in response.splitlines():
        columns = line.split()

        record = record + [
            {"measurement": "fc",
             "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": hostname,
                      "hba": columns[0]},
             "fields": {"rx_bytes": int(columns[2],0)*4, "tx_bytes": int(columns[1],0)*4},
             "time": timestamp
             }
        ]

    ########################

    # Close ssh session
    ssh.ssh_del()        
    logging.debug("Finished core function ssh with args %s" % args)

    # Send Data to InfluxDB
    logging.debug("Data to be sent to DB by fc %s" % record)
    send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    
    logging.debug("Finished func_eternus_cs8000_fc")
