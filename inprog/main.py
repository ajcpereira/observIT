#################################################################################
#                                                                               #
#                       IDENTIFICATION DIVISION                                 #
#                                                                               #
#################################################################################
# This is the main program from the FJ Collector
# it receives inputs from a YAML configfile to collect metrics from
# different sources
#
# This is not a comercial product and it's 'as is' is basically for PoC that a 
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
import sys
import logging
sys.path.append("functions_core")
from functions_core.yaml_validate import read_yaml, create_metric_ip_dicts
import os
import threading

#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################


#################################################################################
#                                                                               #
#                       PROCEDURE DIVISION                                      #
#                                                                               #
#################################################################################

########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################
def run_threaded(job_func, *args):
    job_thread = threading.Thread(target=job_func, args=args)
    job_thread.start()
########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################

########## FUNCTION GET AND CHECK CONFIG FILE  ##################################
def configfile_read():
    if len(sys.argv) == 2:
        try:
            if os.path.isfile(sys.argv[1]):
                config = read_yaml(sys.argv[1])
            else:
                print('No configfile - %s' % sys.argv[1])
                exit(1)
        except Exception as msgerr:
            print("Can't handle configfile - %s - with error - %s" % (sys.argv[1],msgerr))
            exit(1)
    elif len(sys.argv) > 2: 
        print("Only configfile path is needed")
        exit(1)
    else:
        print("You need to specifie the configfile")
        exit(1)
    return config
########## FUNCTION GET AND CHECK CONFIG FILE  ##################################


#################################################################################
#                                                                               #
#                       MAIN                                                    #
#                                                                               #
#################################################################################

if __name__ == "__main__":

    config = configfile_read()
    result_dicts, global_parms = create_metric_ip_dicts(config)
    
    ########## BEGIN - Start Logging Facility #######################################
    logging.basicConfig(filename=global_parms['logfile'], level=global_parms['loglevel'], format='%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s')
    ########## END - Start Logging Facility #########################################    

    ########## BEGIN - Log configfile start processing ##############################
    logging.info("Starting YAML Processing")
    ########## END - Log configfile start processing ################################

    # Print the resulting dictionaries
    for result_dict in result_dicts:
        print(result_dict)
        run_threaded(result_dict['func'], result_dict)