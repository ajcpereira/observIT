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
from functions_core.yaml_validate import read_yaml, AllowedMetrics

#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################

config = read_yaml('config/config4.yaml')

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


########## FUNCTION VALIDATES YAML AND RETURNS DICT #############################
def create_metric_ip_dicts(config):
    result_dicts = []
    global_parms = config.global_parameters
    for system in config.systems:
        for metric in system.config.metrics:
            for ip in system.config.ips:
                ip_dict = vars(ip)
                result_dict = {
                    "name": system.name,
                    "resources_types": system.resources_types,
                    **system.config.parameters.model_dump(),
                    "metric_name": metric.name,
                    "ip": ip.ip,
                    **ip_dict,
                    "func": AllowedMetrics.get_func_name(system.resources_types, metric.name),
                    **global_parms.model_dump()
                }
                result_dicts.append(result_dict)
                
    return result_dicts, global_parms.model_dump()
########## FUNCTION VALIDATES YAML AND RETURNS DICT #############################

#################################################################################
#                                                                               #
#                       MAIN                                                    #
#                                                                               #
#################################################################################

if __name__ == "__main__":

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