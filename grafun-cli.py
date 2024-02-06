########################################################################################################################
#  DO NOT USE!!! UNDER DEVELOPMENT!!!
#
#   name: grafun_cli
#   usage: grafun_cli -c [config file path] [dashboard name prefix]
#       [config file path] : optional config file to build the dashboard (if not present will use the default location)
#       [dashboard name prefix]: Dashboard name prefix, to name the dashboard. Dashboard name will be
#                                 [dashboard name prefix] System Name dashboard
#
#
#
########################################################################################################################


VERSION=0.1

import yaml
import json, requests, logging
import functions_core.yaml_validate
from functions_core.grafana_fun import *



def testes():

    configfile = "config/config.yaml"

    print("Command line collector dashboards generator v", VERSION)

    print("Reading config file:", configfile)
    #config2 = read_yaml(configfile)
    config, orig_mtime, configfile_running = configfile_read(configfile)
    result_dicts, global_parms = create_metric_ip_dicts(config)

    #print(config)
    #print("Create dashboards in grafana server:", config['global_parameters'])
    build_dashboards(config)


    return 1


def build_dashboards_new(config):
    # Dashboards will not be overwrited anymore

    logging.debug("Will build dashboards")
    grafana_api_key = config.global_parameters.grafana_api_key
    grafana_server = config.global_parameters.grafana_server + ":3000"

    systems = data_model_build(config)

    for sys in systems:
        #print(">>", sys)
        #print(sys['system'])
        my_dashboard = create_system_dashboard(sys, config)
        # print(sys['system'], " ", my_dashboard)
        my_dashboard_json = get_dashboard_json(my_dashboard, overwrite=True, message="Updated by fjcollector")
        logging.debug("Created dashboard %s", my_dashboard_json)
        upload_to_grafana(my_dashboard_json, grafana_server, grafana_api_key)


testes()

