import pywbem
from datetime import datetime

# Set up the connection parameters
server_url = 'http://10.36.159.47:5988'  # Replace with your SMI-S server URL
username = 'apereira'                       # Replace with your username
password = 'TBD'                       # Replace with your password

# Connect to the SMI-S server
conn = pywbem.WBEMConnection(
    server_url, 
    (username, password), 
    default_namespace="root/eternus"
    )

def get_volume_iops():
    try:
        instances = conn.EnumerateInstances('FUJITSU_BlockStorageStatisticalData')
        for instance in instances:
            if instance.get('ElementType') == 6:
                volume_name = instance.get('InstanceID')  # Example property for volume name
                read_iops = instance.get('ReadIOs')
                write_iops = instance.get('WriteIOs')
                ReadIOTimeCounter = instance.get("ReadIOTimeCounter")
                timestamp = instance.get('StatisticTime')
                print(f"Volume: {volume_name}, Read IOPS: {read_iops}, Write IOPS: {write_iops} at {timestamp}, ReadIOTimeCounter: {ReadIOTimeCounter}")
#Pag 172

    except Exception as e:
        print(f"Error retrieving volume IOPS: {e}")

def get_thinpool():
    try:
        instances = conn.EnumerateInstances('FUJITSU_ThinProvisioningPool')
        #print(instances)
        for instance in instances:
            print(f"Name: {instance.get('ElementName')}, TotalManagedSpace:{instance.get('TotalManagedSpace')/1024/1024/1024/1024}, Used:{(instance.get('TotalManagedSpace') - instance.get('RemainingManagedSpace'))/1024/1024/1024/1024}")
    except Exception as e:
        print(f"Error retrieving volume IOPS: {e}")

# Execute the functions
#get_cpu_busy_rate()
get_volume_iops()
get_thinpool()