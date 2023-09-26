# Script name: linux-os-srv.py
# Script purpose:
#   Script to collect cpu and mem data from a linux host

from functions_core.netcat import *
from functions_core.secure_connect import *
import re, logging


def send_data(c_params, c_values, str_timestamp, **kwargs):

    str_msg_begin = kwargs['collector_root'] + "." + kwargs['name'] + "." + kwargs['resources_types'] + "." + kwargs['alias'].replace(".", "-") + "."
    for i in range(0, len(c_params)):

        try:
            str_data = str_msg_begin + c_params[i] + " " + str(c_values[i]) + " " + str_timestamp + "\n"
            netcat(str(kwargs['repository']), int(kwargs['repository_port']), kwargs['repository_protocol'], str_data)
            logging.debug("Data sent to repository: %s", str_data)
        except Exception as msgerror:
            logging.error("Failed to send data to repository %s:%s/%s" % kwargs['repository'], kwargs['repository_port'],kwargs['repository_protocol'] )
            return -1



#################################################################################
#
#  linux_os_fs()
#   collects for each filesystem values in GB:
#       "fs.{mount}.available", "fs.{mount}.used", "fs.{mount}.total"

#
#################################################################################
def linux_os_fs(**args):

    # list_data = ["fs.mount", "fs.available", "fs.used", "fs.total"]

    # Filesystem
    # mount available used

    #STR_CMD = "df | tail -n +2 | awk '{print $6, $4, $3, $2}'"
    STR_CMD = "df -x tmpfs | tail -n +2 | awk '{print $6, $4, $3, $2}'"

    logging.info("linux_os_fs: Starting ssh execution to get linux_os_fs filesystem metrics")

    logging.info("linux_os_fs: Connecting to remote host - %s", str(args['ip']))
    logging.info("linux_os_fs: Executing command - %s", STR_CMD)

    try:
        sshcon = Secure_Connect(str(args['ip']), args['bastion'], args['user'], args['host_keys'])
        stdout = sshcon.ssh_run(STR_CMD)
        response = stdout.stdout
        sshcon.ssh_del()

        int_timestamp = int(time.time())
        logging.info("linux_os_fs: Command Result - %s",  response)
        logging.info("linux_os_fs: Finished ssh execution to get linux_os_fs metrics")

        lst_output = response.splitlines()
        for lst_output_line in lst_output :
            list_line = str(lst_output_line).split()
            cdata_info = ["fs."+ re.sub("/", "_dash_", list_line[0])+"."+"available", "fs."+re.sub("/", "_dash_", list_line[0])+"."+"used", "fs."+re.sub("/", "_dash_", list_line[0])+"."+"total"]
            arr_cdata_values = [int(list_line[1])/1024/1024, int(list_line[2])/1024/1024, int(list_line[3])/1024/1024]
            send_data(cdata_info, arr_cdata_values, str(int_timestamp), **args)

    except Exception as msgerror:
        logging.error("linux_os_fs: Failed to connect to %s - %s" % (args['ip'], msgerror))
        return -1

#################################################################################
#
#  linux_os_net()
#   collects for each network interface in status connected values in Mbp:
#       "net.{iface}.rx_mbp", "net.{iface}.tx_mbp"
#
#################################################################################
def linux_os_net(**args):

    # Network
    # interface  rx_bytes tx_bytes

    #STR_CMD = "nmcli device status | awk ' /connected/ {print $1}' | grep -f /dev/stdin /proc/net/dev | awk '{sub(/:/, \"\");print $1, $2, $10}'"
    STR_CMD = "nmcli  -t -f DEVICE con | grep -f /dev/stdin /proc/net/dev | awk '{sub(/:/, \"\");print $1, $2, $10}'"

    logging.info("linux_os_net: Starting ssh execution to get linux_os_net network metrics")

    logging.info("linux_os_net: Connecting to remote host - %s", str(args['ip']))
    logging.info("linux_os_net: Executing command - %s", STR_CMD)

    try:
        sshcon = Secure_Connect(str(args['ip']), args['bastion'], args['user'], args['host_keys'])
        stdout = sshcon.ssh_run(STR_CMD)
        response = stdout.stdout
        sshcon.ssh_del()

        int_timestamp = int(time.time())
        logging.info("linux_os_net: Command Result linux_os_net - %s",  response)
        logging.info("linux_os_net: Finished ssh execution to get metrics")

        lst_output = response.splitlines()
        for lst_output_line in lst_output :
            list_line = str(lst_output_line).split()
            cdata_info = ["net." + list_line[0] + "." + "rx_mbp", "net." + list_line[0] + "." + "tx_mbp"]
            arr_cdata_values = [int(list_line[1])/1024/1024, int(list_line[2])/1024/1024]
            logging.debug ("get_linux_net: network data = %s | %s", cdata_info,arr_cdata_values)
            send_data(cdata_info, arr_cdata_values, str(int_timestamp), **args)

    except Exception as msgerror:
        logging.error("linux_os_net: Failed to connect to %s" % args['ip'])
        return -1

def get_linux_uptime(GPARAMS):

    #under developemnet
    STR_CMD = "awk '{print $1}' /proc/uptime"

    logging.info("Starting ssh execution to get linux-os uptime metrics")

    logging.info("Connecting to remote host - %s", GPARAMS['HOSTNAME'])
    logging.info("Executing command - %s", STR_CMD)

    sshcon = Secure_Connect(GPARAMS['HOSTNAME'], GPARAMS['SSH_BASTION'], GPARAMS['SSH_USER'], GPARAMS['SSH_USER_KEY_FILE'])
    stdout = sshcon.ssh_run(STR_CMD)
    response =stdout.stdout
    sshcon.ssh_del()

    int_timestamp = int(time.time())
    logging.info("Command Result - %s",  response)
    logging.info("Finished ssh execution to get metrics")

    arr_cdata_values = response.split()
    cdata_info = ["uptime"]
    arr_cdata_values[0]=int(arr_cdata_values[0])/86400

    logging.debug ("get_cpuload(): uptime data = %s \ %s", cdata_info,arr_cdata_values)

    #send_data(GPARAMS, cdata_info, arr_cdata_values, ".", str(int_timestamp))
    logging.info("Ended collecting data")




#################################################################################
#
#  linux_os_cpu()
#   collects:
#       cpu.use
#       cpu.iowait
#       cpu.load1m
#       cpu.load5m
#       cpu.load15m
#################################################################################

def linux_os_cpu(**args):

    # Definitions/Constants
    CDATA_INFO = ["cpu.use", "cpu.iowait", "cpu.load1m", "cpu.load5m", "cpu.load15m"]

    STR_CMD = "echo $(vmstat 1 2 | tail -1 | awk '{print $15, $16}') $(cat /proc/loadavg | awk '{print $1, $2, $3}')"

    logging.info("linux_os_cpu: Starting ssh execution to get linux_os_cpu metrics")

    logging.info("linux_os_cpu: Connecting to remote host - %s", str(args['ip']))
    logging.info("linux_os_cpu: Executing command - %s", STR_CMD)

    try:
        ssh = Secure_Connect(str(args['ip']), args['bastion'], args['user'], args['host_keys'])
        stdout = ssh.ssh_run(STR_CMD)
        response = stdout.stdout
        ssh.ssh_del()

        int_timestamp = int(time.time())
        logging.debug("linux_os_cpu: Command Result - %s", response)
        logging.debug("linux_os_cpu: Finished ssh execution to get metrics")

        arr_cdata_values = response.split()

        # convert cpu free to use
        arr_cdata_values[0] = str(100 - int(arr_cdata_values[0]))

        logging.debug("linux_os_cpu: Values array %s", CDATA_INFO)
        logging.debug("linux_os_cpu: Collected values array %s", arr_cdata_values)

        send_data(CDATA_INFO, arr_cdata_values, str(int_timestamp), **args)

        logging.debug("linux_os_cpu: Ended collecting data")

    except Exception as msgerror:
        logging.error("linux_os_cpu: Failed to connect to %s" % args['ip'])
        return -1

###################################################################################
#
#  linux_os_mem()
#       collects memory stats in MB:
#       "mem.total", "mem.used", "mem.free", "mem.shared", "mem.buff", "mem.avail"
###################################################################################
def linux_os_mem(**args):

    # Definitions/Constants
    CDATA_INFO = ["mem.total", "mem.used", "mem.free", "mem.shared", "mem.buff", "mem.avail"]

    STR_CMD = "free -m | grep Mem | awk '{print $2, $3, $4, $5, $6, $7}'"

    logging.info("linux_os_mem: Starting ssh execution to get linux_os_mem metrics")

    logging.info("linux_os_mem: Connecting to remote host - %s", str(args['ip']))
    logging.info("linux_os_mem: Executing command - %s", STR_CMD)

    try:
        ssh = Secure_Connect(str(args['ip']), args['bastion'], args['user'], args['host_keys'])
        stdout = ssh.ssh_run(STR_CMD)
        response = stdout.stdout
        ssh.ssh_del()

        int_timestamp = int(time.time())
        logging.debug("linux_os_mem: Command Result - %s", response)
        logging.debug("linux_os_mem: Finished ssh execution to get metrics")

        arr_cdata_values = response.split()

        logging.debug("linux_os_mem: Values array %s", CDATA_INFO)
        logging.debug("linux_os_mem: Collected values array %s", arr_cdata_values)

        send_data(CDATA_INFO, arr_cdata_values, str(int_timestamp), **args  )

        logging.debug("linux_os_mem: Ended collecting data")

    except Exception as msgerror:
        logging.error("linux_os_mem: Failed to connect to %s" % args['ip'])
        return -1