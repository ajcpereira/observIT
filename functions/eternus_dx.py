from easysnmp import Session
from functions_core.send_influxdb import *

def eternus_dx_cpu(**args):
    # Create an SNMP session to a device
    session = Session(hostname=str(args['ip']), community=str(args['snmp_community']), version=1)

    # We will get the OID version, until now all the rest of the info is the same
    SNMP_MIB_VER = session.get('1.3.6.1.2.1.1.2.0').value[1:]

    timestamp = int(session.get(SNMP_MIB_VER + '.5.1.4.0').value)
 

    nr_cores=[]
    #Perform an SNMP WALK on a subtree
    for item in session.walk(SNMP_MIB_VER + '.5.14.2.1.2'):
        nr_cores = nr_cores + [item.value]

    i = 3
    record=[]
    for core in nr_cores:
         oid = SNMP_MIB_VER + ".5.14.2.1." + str(i)
         i += 1
         for usage in session.walk(oid):
            #print(f"My cpu usage in CM{usage.oid.split('.')[-1]} and core {i-4} is {usage.value}%")            

            record = record + [
                {"measurement": "eternus_dx_cpu",
                "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": args['hostname'],
                         "CM": str(usage.oid.split('.')[-1]), "Core": str(i-4)
                         },
                "fields": {"busyrate": int(usage.value)},
                "time": timestamp
                }
            ]
    
    # Send Data to InfluxDB
    if record:
        logging.debug("Data to be sent to DB by eternus_dx_cpu:\n%s" % record)
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    else:
         logging.warning(f"There is no data to be sent to influxdb, are you in the correct system with the correct metrics?")

    logging.debug("Finished func_eternus_dx_cpu")

def eternus_dx_tppool(**args):
    # Create an SNMP session to a device
    session = Session(hostname=str(args['ip']), community=str(args['snmp_community']), version=1)

    # We will get the OID version, until now all the rest of the info is the same
    SNMP_MIB_VER = session.get('1.3.6.1.2.1.1.2.0').value[1:]

    timestamp = int(session.get(SNMP_MIB_VER + '.5.1.4.0').value)
 

    nr_tppool=[]
    #Perform an SNMP WALK on a subtree
    for item in session.walk(SNMP_MIB_VER + '.14.5.2.1.1'):
        nr_tppool = nr_tppool + [item.value]
    
    record=[]
    for poolnr in nr_tppool:
        tppool_total_mb = int(session.get(str(SNMP_MIB_VER + ".14.5.2.1.3." + str(poolnr))).value)
        tppool_used_mb = int(session.get(str(SNMP_MIB_VER + ".14.5.2.1.4." + str(poolnr))).value)    

        record = record + [
            {"measurement": "eternus_dx_tppool",
            "tags": {"system": args['name'], "resource_type": args['resources_types'], "host": args['hostname'],
                     "TPPOOL_NR": str(poolnr)
                     },
            "fields": {"Total Capacity": int(tppool_total_mb),
                       "Total Used": int(tppool_used_mb)    
            },
            "time": timestamp
            }
        ]
    
    # Send Data to InfluxDB
    if record:
        logging.debug("Data to be sent to DB by eternus_dx_tppool:\n%s" % record)
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    else:
         logging.warning(f"There is no data to be sent to influxdb, are you in the correct system with the correct metrics?")

    logging.debug("Finished func_eternus_dx_tppool")