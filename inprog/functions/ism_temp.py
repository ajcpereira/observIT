from functions_core.netcat import *
import re, os, logging, subprocess, time, requests


def ism_temp(**args):

    logging.debug("Starting func_ism_temp")



    # API addresses
    login_address="https://" + str(args['ip']) + ":" + str(args['ism_port']) + "/ism/api/V2/users/login"
    list_nodes="https://" + str(args['ip']) + ":" + str(args['ism_port']) + "/ism/api/V2/nodes"
    logging.debug(login_address)

    r = requests.post(login_address, json={"IsmBody": {"UserName": args['user'], "Password": str(args['ism_password'])}}, verify=args['ism_secure']).json()

    logging.debug("return requests %s" % r)

    logging.debug(r['IsmBody']['Auth'])
            
    logging.debug("Finished func_ism_temp with args %s" % args)