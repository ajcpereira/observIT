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
#sys.path.append("functions_core")
from functions_core.yaml_validate import read_yaml, create_metric_ip_dicts
from functions.fs_name import fs_name
import os
import threading
import time
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
    orig_mtime=(os.path.getmtime(sys.argv[1]))
    return config, orig_mtime
########## FUNCTION GET AND CHECK CONFIG FILE  ##################################

########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################
def run_threaded(**args):
    print("entered run thread")
    while True:
        print("enter cycle")
        time.sleep(args['poll'])
        job_thread = threading.Thread(target=eval(args['func']), kwargs=args)
        job_thread.start()

########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################


#################################################################################
#                                                                               #
#                       MAIN                                                    #
#                                                                               #
#################################################################################

if __name__ == "__main__":

    config, orig_mtime = configfile_read()
    result_dicts, global_parms = create_metric_ip_dicts(config)
    
    ########## BEGIN - Start Logging Facility #######################################
    logging.basicConfig(filename=global_parms['logfile'], level=global_parms['loglevel'], format='%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s')
    ########## END - Start Logging Facility #########################################    

    ########## BEGIN - Log configfile start processing ##############################
    logging.info("Starting YAML Processing")
    ########## END - Log configfile start processing ################################

    if orig_mtime < os.path.getmtime(sys.argv[1]):
        print('file time changed')

    # Print the resulting dictionaries
    for result_dict in result_dicts:
        threading.Thread(target=run_threaded, kwargs=result_dict).start()

    