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
import threading
sys.path.append("functions")
from functions.fs import func_eternus_icp_fs, func_os_cpu_mem

configfile="config.yaml"

#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################

########## SUPPORTED RESOURCES AND METRICS ######################################
# Relation between resource types and metrics. Also returns the function name
# l_resources_types=["eternus_icp", "linux_os"]
# m_linux_os_metrics=["cpu_mem"], ["func_os_cpu_mem"]
# m_eternus_icp_metrics=["fs"],["func_eternus_icp_fs"]

# Required parameters for function
# p_os_cpu_mem=["name"]
#
# every function must have some parameters as optional, i.e. alias, proxy, sudo, etc

r_resources_types=["eternus_icp", "linux_os"]

# Metric name in 1st list and function name in 2nd list
m_eternus_icp_metrics=["fs", "cpu_mem"],["func_eternus_icp_fs","func_os_cpu_mem"]
m_linux_os_metrics=["cpu_mem"], ["func_os_cpu_mem"]

# Mandatory parameters and the optional parameters
p_func_eternus_icp_fs=["poll", "user", "host_keys", "known_hosts"],["snmp_community", "snmp_port"] 
p_func_os_cpu_mem=["poll", "user", "host_keys", "known_hosts"], ["snmp_community", "snmp_port"]
########## SUPPORTED RESOURCES AND METRICS ######################################

########## GLOBAL PARAMETERS ####################################################
# THEY ARE OVERWRITTEN AFTER READING THE CONFIG FILE                            #
#################################################################################
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

########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################
def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################

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
        param_system_name=system['name']
        for config in system['config']:
            param_resource=config['resources_types']
            parameters = config['parameters']

            for metric in config['metrics']:
                param_metric=metric['name']
                for ip in config['ips']:
                    param_ip=ip['ip']
                    param_alias=ip['alias']
                    
                    ########## VALIDATE RESOURCES AND METRICS FROM CONFIG FILE AND AGAINST OUR ARRAY ##########
                    if param_resource in r_resources_types:
                        if param_metric in eval("m_" + param_resource + "_metrics")[0]:
                            pos_index=eval("m_" + param_resource + "_metrics")[0].index(param_metric)
                            func_name=eval("m_" + param_resource + "_metrics")[1][pos_index]
                            func_array="p_" + func_name
                            command=func_name + "("
                            # Validate Mandatory Parameters
                            for i in range(0,len(eval(func_array)[0])):
                                try:
                                    locals()[eval(func_array)[0][i]]=parameters[eval(func_array)[0][i]]
                                    if i > 0:
                                        command = command + "," + eval(func_array)[0][i]
                                    else:
                                        command = command + eval(func_array)[0][i]
                                except:
                                    print(eval(func_array)[0][i] + " is mandatory for resource " + param_resource + " will terminate execution")
                                    exit(1)
                            # Validate Optional Parameters and if not in config yaml it sets to None
                            for i in range(0,len(eval(func_array)[1])):
                                try:
                                    locals()[eval(func_array)[1][i]]=parameters[eval(func_array)[1][i]]
                                    command = command + "," + eval(func_array)[1][i]
                                except:
                                    locals()[eval(func_array)[1][i]]=None
                                    command = command + "," + eval(func_array)[1][i]
                                    pass
                            command = command + ")"
                            #print(eval(command))
                            #print(command)
                            poll=None
                            schedule.every(locals()['poll']*60).seconds.do(run_threaded, func_eternus_icp_fs(poll))

                        else:
                            print("Metric not valid - %s" % param_metric)
                            exit (1)
                    else:
                        print("Resource not valid - %s" % param_resource)
                        exit (1)
                    ########## VALIDATE RESOURCES AND METRICS FROM CONFIG FILE AND AGAINST OUR ARRAY ##########

########## FUNCTION GET VALUES TO BUILD TASKS FROM CONFIG FILE ##################

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
        schedule.run_pending()
        time.sleep(1)
        if orig_mtime < os.path.getmtime(configfile):
            logging.info("Config File was changed will reload - %s" % time.ctime())
            print("Will reload")
            schedule.clear()
            configdata, orig_mtime=f_readglobalparametersconfigfile()
            f_readconfigfile(configdata)
        