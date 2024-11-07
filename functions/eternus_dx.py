from easysnmp import Session

def eternus_dx_cpu(**args):
    # Create an SNMP session to a device (replace with your device's IP)
    session = Session(hostname='10.36.159.47', community='public', version=1)

    # Perform an SNMP GET
    #item = session.get('1.3.6.1.4.1.211.1.21.1.150.5.14.1.0')
    #print(f'{item.oid}: {item.value}')

    nr_cores=[]
    #Perform an SNMP WALK on a subtree (e.g., 1.3.6.1.2.1.1 for system info)
    for item in session.walk('1.3.6.1.4.1.211.1.21.1.150.5.14.2.1.2'):
        nr_cores = nr_cores + [item.value]

    i = 3
    for core in nr_cores:
         oid = "1.3.6.1.4.1.211.1.21.1.150.5.14.2.1." + str(i)
         i += 1
         for usage in session.walk(oid):
            print(f"My cpu usage in CM{usage.oid.split('.')[-1]} and core {i-4} is {usage.value}%")

