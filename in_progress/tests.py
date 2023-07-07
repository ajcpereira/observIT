#################################################################################
#                                                                               #
#                       IDENTIFICATION DIVISION                                 #
#                                                                               #
#################################################################################
# This is the main program from the Fujitsu Collector
# it receives inputs from a YAML configfile to collect metrics from
# different resources
#
# This is no comercial product and it's 'as is' is basically for PoC that a 
# unique tool can get the most relevant data from a Datacenter and how is easy
# it can be
#
# Also, will allow to the ones intervening in this process to acquire knowledge
# in different protocols and command lines to acquire the needed info


#################################################################################
#                                                                               #
#                       ENVIRONMENT DIVISION                                    #
#                                                                               #
#################################################################################
import yaml
import logging
import time
import os

configfile="config.yaml"

#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################

########## SUPPORTED RESOURCES AND METRICS ######################################
resources_types=["primergy", "primequest", "eternus_icp", "linux_os"]
primergy_metrics=["cpu","mem","fs"]
linux_os_metrics=["cpu", "mem", "fs"]
eternus_icp_metrics=["fs"]
########## SUPPORTED RESOURCES AND METRICS ######################################

########## GLOBAL PARAMETERS ####################################################
global PLATFORM_REPO
global PLATFORM_REPO_PORT
global PLATFORM_REPO_PROTOCOL
global PLATFORM_LOG
global PLATFORM_LOGFILE

PLATFORM_REPO="graphite"
PLATFORM_REPO_PORT=2003
PLATFORM_REPO_PROTOCOL="tcp"
PLATFORM_LOG="INFO"
PLATFORM_LOGFILE="logs/fj-collector.log"
########## GLOBAL PARAMETERS ####################################################

#################################################################################
#                                                                               #
#                       PROCEDURE DIVISION                                      #
#                                                                               #
#################################################################################

########## FUNCTION OPEN YAML FILE AND READ IT ##################################
def readglobalparametersconfigfile():
    with open(configfile, 'r') as f:
        try:
            configdata = yaml.safe_load(f)
            f.close
        except FileNotFoundError:
            print("Sorry, the file %s does not exist" % configfile)
    ########## BEGIN - INITIALIZE GLOBAL VARS ###################################
    global PLATFORM_REPO
    global PLATFORM_REPO_PORT
    global PLATFORM_REPO_PROTOCOL
    global PLATFORM_LOG
    global PLATFORM_LOGFILE
    ########## END - INITIALIZE GLOBAL VARS #####################################

    ########## BEGIN - CREATE CONSTANTS BASED IN GLOBAL PARAMETERS FROM YAML ####
    try:
        PLATFORM_REPO=configdata["global parameters"]["repository"]
        PLATFORM_REPO_PORT=configdata["global parameters"]["repository_port"]
        PLATFORM_REPO_PROTOCOL=configdata["global parameters"]["repository_protocol"]
        PLATFORM_LOG="logging." + configdata["global parameters"]["log"]
        PLATFORM_LOGFILE=configdata["global parameters"]["logfile"]
    except Exception as msg_err:
        logging.error("Error getting global parameters" + " with error " + str(msg_err))
        exit(1)
    ########## END - CREATE CONSTANTS BASED IN GLOBAL PARAMETERS FROM YAML ######
    orig_mtime=(os.path.getmtime(configfile))
    return configdata, orig_mtime
########## FUNCTION OPEN YAML FILE AND READ IT ##################################


########## FUNCTION BUILD TASKS FROM CONFIG FILE ###############################
def readconfigfile(configdata):
#    for systems_line in range(len(configdata['systems'])):
#        for systems_config_line in range(len(configdata['systems'][systems_line]['config'])):
#            for systems_resources_line in range(len(configdata['systems'][systems_line]['config'][systems_config_line]['metrics'])):
#                print(configdata['systems'][systems_line]['name'])
#                print(configdata['systems'][systems_line]['config'][systems_config_line]['resources_types'])
#                print(configdata['systems'][systems_line]['config'][systems_config_line]['metrics'][systems_resources_line]['name'])
#                for param in configdata['systems'][systems_line]['config'][systems_config_line]['parameters']:
#                    print(param['user'])
    for system in configdata['systems']:
        print(system['name'])
        for config in system['config']:
            print(config['resources_types'])
            for metric in config['metrics']:
                print(metric['name'])
            for ip in config['ips']:
                print(ip['ip'], ip['alias'])
            parameters = config['parameters']
            #print(parameters['user'])
            #print(parameters['host_keys'])
            #print(parameters['known_hosts'])
            #print(parameters['poll'])
        print("\n#######################################################\n")


########## FUNCTION BUILD TASKS FROM CONFIG FILE ###############################


########## FUNCTION VALIDATE RESOURCES AND METRICS FROM CONFIG FILE ##########
def validate_resources_metrics(input_resources, input_metrics):
    if input_resources in resources_types:
        print (input_resources)
        if input_metrics in eval(input_resources + "_metrics"):
            print(input_metrics)
        else:
            print("metric not valid - %s" % input_metrics)
    else:
        print("resource not valid - %s" % input_resources)
########## FUNCTION VALIDATE RESOURCES AND METRICS FROM CONFIG FILE ##########




#################################################################################
#                                                                               #
#                       MAIN                                                    #
#                                                                               #
#################################################################################


if __name__ == "__main__":

    configdata, orig_mtime=readglobalparametersconfigfile()

    ########## BEGIN - Start Logging Facility #######################################
    logging.basicConfig(filename=PLATFORM_LOGFILE, level=eval(PLATFORM_LOG))
    ########## END - Start Logging Facility #########################################    

    ########## BEGIN - Log configfile start processing ##############################
    logging.info("Starting YAML Processing - %s" % time.ctime())

    readconfigfile(configdata)
    #validate_resources_metrics(USER_INPUT1, USER_INPUT2)
    ########## END - Log configfile start processing ################################



    while True:
        actual_mtime=os.path.getmtime(configfile)
        if orig_mtime >= os.path.getmtime(configfile):
            print("No change")
            #schedule.run_pending()
        else:
            logging.info("Config File was changed will reload - %s" % time.ctime())
            print("File Change")
            orig_mtime = actual_mtime
            # Stop processes
            # Call readgobbal and readconfig
        time.sleep(10)



      



#      if configdata['solution']['platform'][i]['type'] == "CS8000":
#        PLATFORM=(configdata['solution']['platform'][i]['type'])
#        PLATFORM_NAME=(configdata['solution']['platform'][i]['name'])
#        for z in range(len(configdata['solution']['platform'][i]['resources']['type'])):
#          if configdata['solution']['platform'][i]['resources']['type'][z] == "fs":
#            for x in range(len(configdata['solution']['platform'][i]['resources']['ip'])):
#              var_configdata_current=configdata['solution']['platform'][i]['resources']
#              schedule.every(var_configdata_current["poll"]*60).seconds.do(secure_connect, var_configdata_current["ip"][x], var_configdata_current["proxy"], var_configdata_current["user"], var_configdata_current["type"][z], PLATFORM_HOSTKEYS, PLATFORM_KNOW_HOSTS, PLATFORM, PLATFORM_NAME, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO)
#          elif configdata['solution']['platform'][i]['resources']['type'][z] == "channel":
#            for x in range(len(configdata['solution']['platform'][i]['resources']['ip'])):
#              print("channel" + configdata['solution']['platform'][i]['resources']['ip'])
#          else:
#              print("No valid option for type")
