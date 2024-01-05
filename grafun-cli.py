import yaml
import json, requests, logging
from functions_core.yaml_validate import *
from functions_core.grafana_fun import *

def build_grafana_fun_data_model(config):
    def check_if_metric_exists(system_name, resource_name, metric_name, lst):
        metrics_lst = []
        b_exists = False

        for x in lst:
            if system_name in x['system']:
                for y in x['resources']:
                    if resource_name == y['name']:
                        for z in y['data']:
                            if metric_name == z['metric']:
                                metrics_lst = z['hosts']
                                b_exists = True

        return b_exists, metrics_lst

    def check_if_system_exists(system_name, lst):

        b_result = False
        for x in lst:
            if system_name == x['system']:
                b_result = True

        return b_result

    def check_if_resource_exists(system_name, resource_name, lst):

        b_result = False
        for x in lst:
            if system_name == x['system']:
                for y in x['resources']:
                    if resource_name == y['name']:
                        b_result = True

        return b_result

    def my_update_resource_list(system_name, resource_name, metric_name, lst, dict_metric):

        for x in lst:
            if system_name == x['system']:
                for y in x['resources']:
                    if resource_name == y['name']:
                        for k in y['data']:
                            if metric_name == k['metric']:
                                k.update(dict_metric)

        return lst

    def add_resource(system_name, dict, model):

        local_model = model

        for x in local_model:
            if system_name in x['system']:
                x['resources'].append(dict)
                logging.debug(add_resource.__name__ + ": existing resources are %s", x)

        logging.debug(add_resource.__name__ + ": function result is %s", local_model)

        return local_model

    def my_add_metrics_to_existing_resource_list(system_name, resource_name, dict_metric, model):

        local_model = model

        for x in local_model:
            if system_name == x['system']:
                for y in x['resources']:
                    if resource_name == y['name']:
                        #y['data'].append(dict_metric[0])
                        y['data'] = y['data'] + dict_metric

        return local_model

    logging.debug(build_grafana_fun_data_model.__name__ + ": Config data is - %s", config)
    model_result = []

    try:
        for system in config.systems:
            metric_list = []
            res_list = []
            met_exists = False
            for metric in system.config.metrics:
                host_list = []
                for ip in system.config.ips:
                    #if not ip.alias is None:
                    if ip.alias is not None:
                        hostname = ip.alias
                    else:
                        hostname = str(ip.ip)
                    host_list.append(hostname)

                met_exists, met_hosts_lst = check_if_metric_exists(system.name, system.resources_types, metric.name,
                                                                   model_result)
                logging.debug(build_grafana_fun_data_model.__name__ + ": Existing metric %s and hosts %s", metric.name,
                              met_hosts_lst)
                logging.debug(build_grafana_fun_data_model.__name__ + ": Adding metric %s and hosts %s", metric.name,
                              host_list)
                if met_exists:
                    metric_dict = {"metric": metric.name, "hosts": met_hosts_lst + host_list}
                    logging.debug(build_grafana_fun_data_model.__name__ + ": New metric list %s ",
                                  metric_dict)

                    model_result = my_update_resource_list(system.name, system.resources_types, metric.name,
                                                           model_result, metric_dict)
                    logging.debug(build_grafana_fun_data_model.__name__ + ": New model result %s ",
                                  model_result)
                else:
                    metric_list.append({"metric": metric.name, "hosts": host_list})

                logging.debug(build_grafana_fun_data_model.__name__ + ": Metrics exist %s and metrics list is %s",
                              met_exists, metric_list)

            res_exists = check_if_resource_exists(system.name, system.resources_types, model_result)

            if res_exists and not met_exists:
                logging.debug(
                    build_grafana_fun_data_model.__name__ +
                    ": Resource exist=%s and metrics exist=%s metrics list is %s model_result %s",
                    res_exists, met_exists, metric_list, model_result)
                model_result = my_add_metrics_to_existing_resource_list(system.name, system.resources_types,
                                                                        metric_list, model_result)

            if not res_exists:
                logging.debug(
                    build_grafana_fun_data_model.__name__ + ": Resource %s do not exists but system %s exists",
                    system.resources_types, system.name)
                res_list.append({"name": system.resources_types, "data": metric_list})

            if check_if_system_exists(system.name, model_result) and not res_exists:
                logging.debug(build_grafana_fun_data_model.__name__ + ": System exists - %s", model_result)
                model_result = add_resource(system.name, {"name": system.resources_types, "data": metric_list},
                                            model_result)

            # System
            if not check_if_system_exists(system.name, model_result) and not res_exists:
                model_result.append(
                    {"system": system.name, "resources": res_list, "poll": system.config.parameters.poll})

            logging.debug(build_grafana_fun_data_model.__name__ + ": Model is - %s", model_result)
    except Exception as msgerror:
        logging.error(
            build_grafana_fun_data_model.__name__ +
            ": Unexpected error creating grafana_fun data model - %s" % msgerror)
        return -1

    logging.debug(build_grafana_fun_data_model.__name__ + ": grafana_fun data model is - %s", model_result)

    return model_result

def system_exists(sys_name, dict):

    for sys in dict:
        # print("system exists ", sys)
        if sys['system'] == sys_name:
            return sys

    return None

def new_build_autodash_datamodel(config):

    json_dict = json.loads(config.model_dump_json())
    d_model = []

    print("Complete JSON", json_dict)

    for sys in json_dict['systems']:
        # print("1-",sys['name'], sys['resources_types'])
        d_sys = system_exists(sys['name'], d_model)
        if d_sys == None:
            print(sys['name'], " Naõ existe")
            new_d_sys = True
            d_sys = {'system': sys['name'], 'resources': [], 'poll': 1}
        else:
            new_d_sys = False
            print(sys['name'], " existe")

        # print("2-",d_sys)
        d_res = {'name': sys['resources_types'],'data': []}
        # print("3-",d_res)
        for metrics in sys['config']['metrics']:
            # print(metrics['name'])
            d_metric = {'metric': metrics['name'], 'hosts': []}
            for host in sys['config']['ips']:
                d_metric['hosts'] = d_metric['hosts'] + [host['alias']]
                # print(d_metric)
            d_res['data'] = d_res['data'] + [d_metric]
        print("4-", d_res)
        d_sys['resources'] = d_sys['resources'] + [d_res]
        print("5-",d_sys)
        if new_d_sys:
            d_model = d_model + [d_sys]
        # print("6-", d_model)
        # print("-----------------------")

    print ("Data Model is: ", d_model)
    return d_model


def testes():

    print("testes ao grafana data model")
    configfile = "config/config.yaml"


    config = read_yaml(configfile)

    build_dashboards_new(config)


    return 1

    json_dict = json.loads(read_yaml(configfile).model_dump_json())

    # print(json_dict)

    d_sys = []
    for sys in json_dict['systems']:
        # print(sys['name'], sys['resources_types'])
        d_res = {'name': sys['resources_types'],'data': []}
        # print(d_res)
        for metrics in sys['config']['metrics']:
            # print(metrics['name'])
            d_metric = {'metric': metrics['name'], 'hosts': []}
            for host in sys['config']['ips']:
                d_metric['hosts'] = d_metric['hosts'] + [host['alias']]
                # print(d_metric)
            d_res['data'] = d_res['data'] + [d_metric]
        d_sys = d_sys + [d_res]
        print(d_sys)
        print("-----------------------")

    return 0

def build_dashboards_new(config):
    # Dashboards will not be overwrited anymore

    logging.debug("Will build dashboards")
    grafana_api_key = config.global_parameters.grafana_api_key
    grafana_server = config.global_parameters.grafana_server + ":3000"

    systems = new_build_autodash_datamodel(config)

    for sys in systems:
        print(">>", sys)
        print(sys['system'])
        my_dashboard = create_system_dashboard(sys, config)
        my_dashboard_json = get_dashboard_json(my_dashboard, overwrite=True, message="Updated by fjcollector")
        logging.debug("Created dashboard %s", my_dashboard_json)
        upload_to_grafana(my_dashboard_json, grafana_server, grafana_api_key)


testes()

