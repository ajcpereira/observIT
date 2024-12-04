import os, logging, subprocess, time, re
import pandas as pd
from io import StringIO
from functions_core.send_influxdb import *
from functions_core.SshConnect import *  

# The key must be generated with ssh-keygen -t rsa -N ""
# ssh-keygen -e -f ~/.ssh/id_rsa.pub > id_rsa.pub.ietf
# Your ~/.ssh/config should look like:
#Host *
#    Ciphers=aes128-cbc,aes256-cbc
#    HostKeyAlgorithms=+ssh-rsa
#    PubkeyAcceptedKeyTypes=+ssh-rsa
#signing using ssh-rsa SHA256

def eternus_dx_host_io(**args):

    logging.debug("Starting func_eternus_dx_host_io")
    
    # Organize the args from ip calling specific function     

    # Open ssh session
    try:
        ssh=Secure_Connect(str(args['ip']),args['bastion'],args['user'],args['host_keys'])
    except Exception as msgerror:
        logging.error(f"Failed to connect to {args['ip']} with error: {msgerror}")
        ssh.ssh_del()
        return -1
    
    logging.debug("This is my ssh session from the Class Secure_Connect %s" % ssh)
    

    ########## CHECKING IF PERFORMANCE IS ENABLED ###########################        
    try:
        cmd1="show performance"
        logging.debug(f"Command Line 1 - {cmd1}")
        stdout = ssh.ssh_run(cmd1)
        response = stdout.stdout
        logging.debug(f"Output of Command Line 1:\n {response}")
    except Exception as msgerror:
        logging.error(f"Failed the cmd execution in {args['ip']} with error {msgerror}")
        ssh.ssh_del()
        return -1

    #Status    [ON]
    #Interval  [300sec]

    df = pd.DataFrame(response)

    # Check if the status is 'ON'
    if df['Status'].iloc[0] == 'ON':
        logging.debug(f"Status is ON")
    else:
        logging.error(f"Status is not ON")
        ssh.ssh_del()
        return -1

    ########## WILL EXECUTE MAIN SSH COMMANDS ###########################        
    try:
        cmd1="show performance -type host-io"
        logging.debug(f"Command Line 1 - {cmd1}")
        stdout = ssh.ssh_run(cmd1)
        response = stdout.stdout
        logging.debug(f"Output of Command Line 1:\n {response}")
    except Exception as msgerror:
        logging.error(f"Failed the cmd execution in {args['ip']} with error {msgerror}")
        ssh.ssh_del()
        return -1

    timestamp = int(time.time())

    # Use StringIO to simulate a file
    df = pd.read_csv(StringIO(response), delim_whitespace=True, skiprows=3)

    # Extract the required columns without headers
    extracted_columns = df.iloc[:, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]].to_numpy()

    record = []
    for index, row in extracted_columns.iterrows():

        record = record + [
            {"measurement": "host-io",
            "tags": {
                "system": args['name'], 
                "resource_type": args['resources_types'], 
                "host": args['hostname'],
                "Name": row[1]
            },
            "fields": {
                "IO Reads": row[2],
                "IO Writes": row[3],
                "Throughput Read": row[4],
                "Throughput Write": row[5],
                "Response Time Read": row[6],
                "Response Time Write": row[7],
                "Processing Time Read": row[8],
                "Processing Time Write": row[9],
                "Cache Hit Rate Read": row[10],
                "Cache Hit Rate Write": row[11],
                "Prefetch": row[12],
            },
            "time": timestamp
            }
        ]
        #Send
    
    # Send Data to InfluxDB
    if record:
        logging.debug("Data to be sent to DB by host_io:\n%s" % record)
        send_influxdb(str(args['repository']), str(args['repository_port']), args['repository_api_key'], args['repo_org'], args['repo_bucket'], record)
    else:
         logging.warning(f"There is no data to be sent to influxdb, are you in the correct system with the correct metrics?")
    logging.debug("Finished func_eternus_dx_host_io")
