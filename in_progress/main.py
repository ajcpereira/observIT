#################################################################################
#                                                                               #
#                       IDENTIFICATION DIVISION                                 #
#                                                                               #
#################################################################################
# This is the main program from the FJ Collector
# it receives inputs from a YAML configfile to collect metrics from
# different resources
#
# This is no comercial product and it's 'as is' is basically for PoC that a 
# unique tool can get the most relevant data from a Datacenter and how easy
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
import sys
import schedule
sys.path.append("functions")
from functions.secure_connect import secure_connect

configfile="config.yaml"

#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################

########## SUPPORTED RESOURCES AND METRICS ######################################
# Relation between metrics and function name
# primergy_metrics=["cpu","mem","fs"],["func_lx_cpu", "func_lx_mem", "func_lx_fs"]
# eternus_icp_metrcs=["fs"],["func_cs_fs"]

# Required parameters for function
# func_cs_fs=["user", "know_hosts", "host_keys", "poll"]
# func_lx_mem=["snmp_community", "user", "poll"]

# every function must have alias as optional

l_resources_types=["primergy", "primequest", "eternus_icp", "linux_os"]
primergy_metrics=["cpu","mem","fs"]
linux_os_metrics=["cpu", "mem", "fs"]
eternus_icp_metrics=["fs"],["func_system_name","func_ip","func_alias", "func_pool", "func_bastion", "func_user", "func_metric", "func_host_keys", "func_know_hosts", "func_use_sudo","PLATFORM_REPO","PLATFORM_REPO_PORT","PLATFORM_REPO_PROTOCOL","PLATFORM_LOG","PLATFORM_LOGFILE"]

########## SUPPORTED RESOURCES AND METRICS ######################################

########## GLOBAL PARAMETERS ####################################################
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
def f_readglobalparametersconfigfile():
    ########## BEGIN - READ YAML FILE ###########################################
    with open(configfile, 'r') as f:
        try:
            configdata = yaml.safe_load(f)
            f.close
        except FileNotFoundError:
            print("Sorry, the file %s does not exist" % configfile)
    ########## END - READ YAML FILE #############################################

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


########## FUNCTION GET VALUES TO BUILD TASKS FROM CONFIG FILE ##################
def f_readconfigfile(configdata):
    for system in configdata['systems']:
        func_system_name=system['name']
        for config in system['config']:
            func_resource=config['resources_types']
            for metric in config['metrics']:
                func_metric=metric['name']
            for ip in config['ips']:
                func_ip=ip['ip']
                func_alias=ip['alias']
            parameters = config['parameters']
            if 'host_keys' in parameters:
                func_host_keys=parameters['host_keys']
            if 'user' in parameters:
                func_user=parameters['user']
            if 'know_hosts' in parameters:
                func_know_hosts=parameters['know_hosts']
            if 'poll' in parameters:
                func_poll=parameters['poll']
            if 'use_sudo' in parameters:
                func_use_sudo=parameters['use_sudo']

########## FUNCTION GET VALUES TO BUILD TASKS FROM CONFIG FILE ##################


########## FUNCTION VALIDATE RESOURCES AND METRICS FROM CONFIG FILE ##########
def f_validate_resources_metrics(input_resources, input_metrics):
    if input_resources in l_resources_types:
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

    configdata, orig_mtime=f_readglobalparametersconfigfile()

    ########## BEGIN - Start Logging Facility #######################################
    logging.basicConfig(filename=PLATFORM_LOGFILE, level=eval(PLATFORM_LOG))
    ########## END - Start Logging Facility #########################################    

    ########## BEGIN - Log configfile start processing ##############################
    logging.info("Starting YAML Processing - %s" % time.ctime())

    f_readconfigfile(configdata)

    ########## END - Log configfile start processing ################################

    while True:
        actual_mtime=os.path.getmtime(configfile)
        if orig_mtime >= os.path.getmtime(configfile):
            print("No change")
            # schedule.run_pending()
        else:
            logging.info("Config File was changed will reload - %s" % time.ctime())
            # schedule.clear()
            # configdata, orig_mtime=f_readglobalparametersconfigfile()
            # f_readconfigfile(configdata)
        time.sleep(10)
