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
import sys, os, logging, time
from threading import Thread, Event
from functions_core.yaml_validate import *
from functions_core.grafana_fun import *
from functions_core.SshConnect import *
from functions_core.utils import *
from functions import *


#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################

configfile = "config/config.yaml"
event = Event()

#################################################################################
#                                                                               #
#                       PROCEDURE DIVISION                                      #
#                                                                               #
#################################################################################

########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################

def run_threaded(**args) -> None:
    
    while True:
        if 'control' in args:
            event.wait(60)
            logging.debug("Will run managed sessions")
            if event.is_set():
                logging.debug("#### Exited run_thread for Managed Sessions ####")
                break
            with Secure_Connect.global_lock:
                Secure_Connect.manage_sessions(None)
        else:
            args=args_setup(args)
            event.wait(timeout=args['poll']*60)
            logging.debug("Will run_thread with %s" % args)
            if event.is_set():
                logging.debug("#### Exited run_thread ####")
                break
            Thread(target=eval(args['func']), kwargs=args).start()
########## FUNCTION LAUNCH A THREAD FOR EACH SCHEDULE ###########################

########## FUNCTION FOR EACH METRIC LAUNCH THREADS  #############################

def launch_thread(result_dicts):
    for result_dict in result_dicts:
        logging.debug("Will launch thread %s" % result_dict)
        Thread(target=run_threaded, kwargs=result_dict).start()
    # Will add a Thread to check ssh sessions
    Thread(target=run_threaded, kwargs={'control': 'yes'}).start()

########## FUNCTION FOR EACH METRIC LAUNCH THREADS  #############################

#################################################################################
#                                                                               #
#                       MAIN                                                    #
#                                                                               #
#################################################################################

if __name__ == "__main__":

    ########## BEGIN FUNCTIONS IN YAML_VALIDATE  ################################    
    config, orig_mtime, configfile_running = configfile_read(configfile)
    result_dicts, global_parms = create_metric_ip_dicts(config)
    ########## END FUNCTIONS IN YAML_VALIDATE  ##################################    


    ########## BEGIN - Start Logging Facility ###################################
    logging.basicConfig(filename=global_parms['logfile'], level=eval("logging."+global_parms['loglevel']), format='%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s', force=True)
    ########## END - Start Logging Facility #####################################    

    ########## BEGIN - Log configfile start processing ##########################
    logging.info("################ Starting Collector ################")
    ########## END - Log configfile start processing ############################

    logging.debug("Will print the dict that will be used: %s" % result_dicts)

    launch_thread(result_dicts)

    if config.global_parameters.auto_fungraph:
        build_dashboards(config)
    

    while True:
        time.sleep(1)

        if orig_mtime < os.path.getmtime(configfile_running):
            logging.info("Configfile changed, will reload")

            event.set()
            
            orig_mtime = os.path.getmtime(configfile_running)
            config, orig_mtime, configfile_running = configfile_read(configfile)
            result_dicts, global_parms = create_metric_ip_dicts(config)


            logging.debug("Configfile changed, will reload with %s" % result_dicts)

            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            try:             
                logging.basicConfig(filename=global_parms['logfile'], level=eval("logging."+global_parms['loglevel']), format='%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s', force=True)
            except Exception as msgerr:
                logging.fatal("Failed to change logging basicConfig %s" % msgerr)
                sys.exit()
            
            time.sleep(5)
            event.clear()
            launch_thread(result_dicts)
            if config.global_parameters.auto_fungraph:
                build_dashboards(config)
            logging.info("Configfile reloaded")
            logging.debug("Configfile reloaded")