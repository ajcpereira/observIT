import time
from functions_core.HttpConnect import *
from functions_core.send_influxdb import *
from functions_core.utils import *



def powerstore_node(**args):


    password = decode_base64(args['powerstore_pwd64'])
    logging.debug(f"Arguments are url {args['powerstore_url']}, user {args['powerstore_user']} pass {args['powerstore_pwd64'][4]} and unsucure {args['powerstore_unsecured']}")

    http_client = HttpConnect(args['powerstore_url'], args['powerstore_user'], password, args['powerstore_unsecured'])
    #
    # # Get the node list from Powerstore API
    response = http_client.get('api/rest/node')
    #
    dell_emc_token = response.headers['DELL-EMC-TOKEN']
    #
    #
    if response is None:
        logging.error(f"Error Retrieving node list from URL {args['powerstore_url']}{'api/rest/node'}")
        return -1

    nodes = response.json()

    #nodes = [ { "id": "N1" }, { "id": "N2" } ]

    logging.debug(f"Node Members list is {nodes}")


    for node in nodes:

        # Intervals = Best_Available, Five_Sec, Twenty_Sec, Five_Mins, One_Hour, One_Day
        post_params = {"entity": "performance_metrics_by_node", "entity_id": node['id'], "interval": 'Twenty_Sec'}
        logging.debug(f"Post Parameters {post_params}")

        # header_params = "DELL-EMC-TOKEN: " + dell_emc_token
        response = http_client.post('api/rest/metrics/generate', post_params, {"DELL-EMC-TOKEN": dell_emc_token}) 

        if response is None:
            logging.error(f"Error Retrieving performance data for node {node['id']} {args['powerstore_url']}/api/rest/metrics/generate")
            return -1

        response_json = response.json()


        perfdata = response_json[-1]

        influxdb_record = [{
             "measurement": "powerstore_node",
             "tags": {
                 "system": args['name'],
                 "resource_type": args['resources_types'],
                 "host": args['hostname'],
                 "node_id": node['id']
             },
             "fields": {
                "io_workload_cpu_utilization": perfdata['io_workload_cpu_utilization'],
                "avg_read_latency": perfdata['avg_read_latency'],
                "avg_write_latency": perfdata['avg_write_latency'],
                "read_iops": perfdata['read_iops'],
                "write_iops": perfdata['write_iops'],
                "read_bandwidth": perfdata['read_bandwidth'],
                "write_bandwidth": perfdata['write_bandwidth'],
                "total_bandwidth": perfdata['total_bandwidth'],
                "total_iops": perfdata['total_iops'],
                "avg_latency": perfdata['avg_latency'],
             },
             "time": perfdata['timestamp']
         }
        ]

        logging.debug(f"Data to be sent to influxdb {influxdb_record}")

        send_influxdb(
            str(args['repository']),
            str(args['repository_port']),
            args['repository_api_key'],
            args['repo_org'],
            args['repo_bucket'],
            influxdb_record
        )

    http_client.close()

def powerstore_space(**args):


    password = decode_base64(args['powerstore_pwd64'])
    logging.debug(f"Arguments are url {args['powerstore_url']}, user {args['powerstore_user']} pass {args['powerstore_pwd64'][4]} and unsucure {args['powerstore_unsecured']}")

    http_client = HttpConnect(args['powerstore_url'], args['powerstore_user'], password, args['powerstore_unsecured'])

    # # Get the Appliance list from Powerstore API
    response = http_client.get('api/rest/appliance')

    dell_emc_token = response.headers['DELL-EMC-TOKEN']

    if response is None:
        logging.error(f"Error Retrieving Appliance list from URL {args['powerstore_url']}{'api/rest/appliance'}")
        return -1

    appliances = response.json()

    logging.debug(f"Appliance Members list is {appliances}")

    for appliance in appliances:

        # Intervals = Best_Available, Five_Sec, Twenty_Sec, Five_Mins, One_Hour, One_Day
        post_params = {"entity": "space_metrics_by_appliance", "entity_id": appliance['id'], "interval": 'Best_Available'}
        logging.debug(f"Post Parameters {post_params}")

        # header_params = "DELL-EMC-TOKEN: " + dell_emc_token
        response = http_client.post('api/rest/metrics/generate', post_params, {"DELL-EMC-TOKEN": dell_emc_token}) 

        if response is None:
            logging.error(f"Error Retrieving space for appliance {appliance['id']} {args['powerstore_url']}/api/rest/metrics/generate")
            return -1

        response_json = response.json()


        perfdata = response_json[-1]

        influxdb_record = [{
             "measurement": "powerstore_space",
             "tags": {
                 "system": args['name'],
                 "resource_type": args['resources_types'],
                 "host": args['hostname'],
                 "appliance_id": appliance['id']
             },
             "fields": {
                "logical_provisioned": perfdata['logical_provisioned'],
                "logical_used": perfdata['logical_used'],
                "physical_total": perfdata['physical_total'],
                "physical_used": perfdata['physical_used'],
                "data_physical_used": perfdata['data_physical_used'],
                "efficiency_ratio": perfdata['efficiency_ratio'],
                "data_reduction": perfdata['data_reduction'],
                "system_free_space": perfdata['system_free_space'],
             },
             "time": perfdata['timestamp']
         }
        ]

        logging.debug(f"Data to be sent to influxdb {influxdb_record}")

        send_influxdb(
            str(args['repository']),
            str(args['repository_port']),
            args['repository_api_key'],
            args['repo_org'],
            args['repo_bucket'],
            influxdb_record
        )

    http_client.close()