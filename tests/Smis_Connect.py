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
    conn = pywbem.WBEMConnection(
        storage_url, 
        (username, password), 
        default_namespace='root/eternus'
        )
 
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
password = "apereirA#2024"


volume_names = get_eternus_volume_names(storage_url, username, password)
print("Volume Names:", volume_names) 

#smis_connect(storage_url, username, password)
