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
from functions_core.yaml_validate import create_metric_ip_dicts, configfile_read
from functions.fs_name import fs_name
import os
from threading import Thread, Event
import time
#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################

configfile_default = "config/config.yaml"

#################################################################################
#                                                                               #
#                       PROCEDURE DIVISION                                      #
#                                                                               #
#################################################################################

########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################
def run_threaded(event: Event, **args) -> None:
    while True:
        print("enter cycle")
        time.sleep(args['poll']*60)
        if event.is_set():
            print("Will exit thread")
            break
        else:
            print("will run thread")
            job_thread = Thread(target=eval(args['func']), kwargs=args)
            job_thread.start

########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################

########## FUNCTION FOR EACH METRIC LAUNCH THREADS  #############################
def launch_thread(result_dicts):
    for result_dict in result_dicts:
        print(result_dict)
        Thread(target=run_threaded, args=(event,), kwargs=result_dict).start()
########## FUNCTION FOR EACH METRIC LAUNCH THREADS  #############################

#################################################################################
#                                                                               #
#                       MAIN                                                    #
#                                                                               #
#################################################################################

if __name__ == "__main__":

    config, orig_mtime, configfile_running = configfile_read(sys.argv, configfile_default)
    result_dicts, global_parms = create_metric_ip_dicts(config)
    
    ########## BEGIN - Start Logging Facility #######################################
    logging.basicConfig(filename=global_parms['logfile'], level=global_parms['loglevel'], format='%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s')
    ########## END - Start Logging Facility #########################################    

    ########## BEGIN - Log configfile start processing ##############################
    logging.info("Starting YAML Processing")
    ########## END - Log configfile start processing ################################


    event = Event()
    
    launch_thread(result_dicts)

    while True:
        time.sleep(1)

        if orig_mtime < os.path.getmtime(configfile_running):
            print("will set event")
            orig_mtime = os.path.getmtime(configfile_running)
            event.set()
            config, orig_mtime, configfile_running = configfile_read(sys.argv, configfile_default)
            result_dicts, global_parms = create_metric_ip_dicts(config)
            print("will wait before relaunch")
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            logging.basicConfig(filename=global_parms['logfile'], level=global_parms['loglevel'], format='%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s')
            time.sleep(10)
            event.clear()
            launch_thread(result_dicts)


            