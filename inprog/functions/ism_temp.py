from functions_core.netcat import *
import re, logging, requests, urllib3
from dateutil import parser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ism_temp(**args):

    logging.debug("Starting func_ism_temp")

    if args['alias']:
        hostname = args['alias']
    else:
        hostname = str(args['ip']).replace(".","-dot-")


    # API addresses
    login_ism_url="https://" + str(args['ism_server']) + ":" + str(args['ism_port']) + "/ism/api/V2/users/login"
    list_nodes_url="https://" + str(args['ism_server']) + ":" + str(args['ism_port']) + "/ism/api/v2/nodes"
    get_item_temp="https://" + str(args['ism_server']) + ":" + str(args['ism_port']) + "/ism/api/v2/nodes/monitor/items?nodeid="
    get_temp_hist="https://" + str(args['ism_server']) + ":" + str(args['ism_port']) + "/ism/api/v2/nodes/monitor/items/"

    login_ism = requests.post(login_ism_url, json={"IsmBody": {"UserName": args['user'], "Password": str(args['ism_password'])}}, verify=args['ism_secure']).json()

    auth_key=login_ism['IsmBody']['Auth']

    list_nodes = requests.get(list_nodes_url, headers={"X-Ism-Authorization": auth_key }, verify=args['ism_secure']).json()

    for nodes in list_nodes['IsmBody']['Nodes']:
        if nodes['IpAddress'] == str(args['ip']):
            list_nodes_url = get_item_temp + str(nodes['NodeId'])

            temp_item = requests.get(list_nodes_url, headers={"X-Ism-Authorization": auth_key }, verify=args['ism_secure']).json()

            logging.debug(temp_item['IsmBody']['Items'][0]['ItemId'])

            get_temp_hist = get_temp_hist + str(temp_item['IsmBody']['Items'][0]['ItemId']) + "/history?count=1"

            temp_hist = requests.get(get_temp_hist, headers={"X-Ism-Authorization": auth_key }, verify=args['ism_secure']).json()

            rackid = nodes['RackInfo']['RackId']
            
            temp = temp_hist['IsmBody']['Records'][0]['Value']
            timetemp = temp_hist['IsmBody']['Records'][0]['Timestamp']
            ismtimestamp = parser.parse(timetemp).timestamp()

            logging.debug("Node ID %s" % nodes['NodeId'])
            logging.debug("Rack ID %s" % nodes['RackInfo']['RackId'])
            logging.debug("TimeStamp %s" % temp_hist['IsmBody']['Records'][0]['Timestamp'])
            logging.debug("Temp Value %s" % temp_hist['IsmBody']['Records'][0]['Value'])

            netcat(args['repository'], args['repository_port'], args['repository_protocol'],  str(args['name']) + "." + str(args['resources_types']) + "." + hostname + "." + "temp" + "." + "rackid" + "." + str(rackid) + "." + "temperature" + " " + str(temp) + " " + str(ismtimestamp) + "\n")
            
    logging.debug("Finished func_ism_temp with args %s" % args)