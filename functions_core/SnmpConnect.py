from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, nextCmd
import sys

def walk(host, oid, timeout=1, retries=3):
    results = []
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget((host, 161), timeout=timeout, retries=retries),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    ):
        if errorIndication:
            print(errorIndication, file=sys.stderr)
            return None
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'),
                  file=sys.stderr)
            return None
        else:
            for varBind in varBinds:
                # Each varBind is a tuple of (OID, value)
                results.append(varBind)

    return results

# Example usage
data = walk('10.36.159.47', '1.21.1.150')
if data:
   for item in data:
       print(item)
