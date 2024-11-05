import pywbem
 
def smis_connect(storage_url, username, password, namespace='root/interop'):
    """
    Connect to an SMI-S compliant storage system and retrieve basic information.
    :param storage_url: The URL or IP address of the storage (e.g., "https://eternus.fujitsu.local")
    :param username: Username for accessing the storage
    :param password: Password for accessing the storage
    :param namespace: WBEM namespace to access (default is 'root/interop')
    :return: A list of dictionaries containing information on available storage pools
    """
    try:
        # Set up connection to the SMI-S service
        conn = pywbem.WBEMConnection(
            storage_url,
            (username, password),
            default_namespace=namespace,
            no_verification=True  # Ignore SSL verification (use only if necessary)
        )
 
        # Retrieve all storage pools as an example
        storage_pools = conn.EnumerateInstances('CIM_StoragePool')
        # Process and print storage pool information
        pool_info = []
        for pool in storage_pools:
            pool_details = {
                "InstanceID": pool["InstanceID"],
                "ElementName": pool["ElementName"],
                "TotalManagedSpace": pool["TotalManagedSpace"],
                "RemainingManagedSpace": pool["RemainingManagedSpace"]
            }
            pool_info.append(pool_details)
            print(f"Storage Pool: {pool_details}")
        return pool_info
 
    except pywbem.Error as e:
        print(f"SMI-S Connection Error: {e}")
        return None
import pywbem
 
def get_eternus_volume_names(storage_url, username, password):
    """
    Retrieve the list of volume names from a Fujitsu ETERNUS storage system using SMI-S.
    Parameters:
        storage_url (str): URL of the ETERNUS SMI-S server.
        username (str): Username for the SMI-S service.
        password (str): Password for the SMI-S service.
 
    Returns:
        List[str]: List of volume names.
    """
    conn = pywbem.WBEMConnection(storage_url, (username, password), default_namespace='root/eternus')
 
    # Retrieve instances of the FUJITSU_StorageVolume class
    try:
        volume_instances = conn.EnumerateInstances('FUJITSU_StorageVolume')
        volume_names = [vol['ElementName'] for vol in volume_instances if 'ElementName' in vol]
        return volume_names
    except pywbem.Error as e:
        print(f"An error occurred: {e}")
        return []
 
 
# Usage example
storage_url = "http://10.36.159.47:5988"
username = "apereira"
password = "NOPWD"

volume_names = get_eternus_volume_names(storage_url, username, password)
print("Volume Names:", volume_names) 

#smis_connect(storage_url, username, password)
