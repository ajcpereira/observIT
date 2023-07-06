# Script name: linux-os-srv.py
# Script purpose:
#   Script to collect cpu and mem data from a linux host
#   Collected values are:
#   cpu_idle_percent cpu_iowait_percent memtotal memused memfree memshared  membuff/cache memavailable
#   Linux command returns cpu usage % and Iowait %
#   CPU: These are percentages of total CPU time.
#     id: Time spent idle.  Prior to Linux 2.5.41, this includes IO-wait time.
#     wa: Time spent waiting for IO.  Prior to Linux 2.5.41, included in idle.
#   MEM
#       total  Total usable memory (MemTotal and SwapTotal in
#              /proc/meminfo). This includes the physical and swap memory
#              minus a few reserved bits and kernel binary code.
#       used   Used or unavailable memory (calculated as total -
#             available)
#       free   Unused memory (MemFree and SwapFree in /proc/meminfo)
#       shared Memory used (mostly) by tmpfs (Shmem in /proc/meminfo)
#       buffers
#              Memory used by kernel buffers (Buffers in /proc/meminfo)
#       cache  Memory used by the page cache and slabs (Cached and
#              SReclaimable in /proc/meminfo)
#       buff/cache
#              Sum of buffers and cache
#       available
#              Estimation of how much memory is available for starting
#              new applications, without swapping. Unlike the data
#              provided by the cache or free fields, this field takes
#              into account page cache and also that not all reclaimable
#              memory slabs will be reclaimed due to items being in use
#              (MemAvailable in /proc/meminfo, available on kernels 3.14,
#              emulated on kernels 2.6.27+, otherwise the same as free)

import time
import logging
import os


def format_cdata(c_params, c_values, str_separator, int_timestamp):

    str_data = ""
    for i in range(0, 8):
        str_data = str_data + c_params[i] + str_separator + str(c_values[i]) + str_separator
    str_data = str_data + str(int_timestamp) + "\n"
    return str_data


def linux_os_cpu():

    str_command = "echo $(vmstat 1 2 | tail -1 | awk '{print $15, $16}')"

    return str_command


def linux_os_srv():

    # Definitions/Constants
    CDATA_INFO = ["cpu_usage_percent", "cpu_iowait_percent", "mem_total", "mem_used", "mem_free", "mem_shared", "mem_buff", "mem_avail"]

    # These are simulated variables, must be deleted in final code
    PLATFORM = "Linux"
    PLATFORM_NAME = "CS_IDP"
    PLATFORM_TYPE = "linux-os"
    hostname = "srv01.lab.local"

    #OUTPUT FORMAT is (mem values in MBytes):
    # cpu_idle_percent cpu_iowait_percent memtotal memused memfree memshared  membuff/cache memavailable

    STR_CMD = "echo $(vmstat 1 2 | tail -1 | awk '{print $15, $16}') $(free -m | grep Mem | awk '{print $2, $3, $4, $5, $6, $7}')"
    logging.info("%s : Starting ssh execution to get linux-os-cpu metrics", time.ctime())
    logging.debug("%s : Command Line - %s", time.ctime(), STR_CMD)
    print("executing command:", STR_CMD)
    response = os.popen(STR_CMD).read()
    int_timestamp = int(time.time())
    logging.debug("%s : Output of Command Line - %s", time.ctime(), response)
    logging.info("%s : Finished ssh execution to get metrics", time.ctime())

    print("command response (%usage %iowait):", response)

    arr_cdata_values = response.split()
    arr_cdata_values[0] = str(100 - int(arr_cdata_values[0]))
    netcat_str = str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(PLATFORM_TYPE) + "." + hostname.replace(".", "-")+"." + format_cdata(CDATA_INFO, arr_cdata_values, ".", int_timestamp)

    logging.debug("%s : Values sent to grafana - %s", time.ctime(), netcat_str)
    #print("CPU Use%", CpuUsage, "CPU IoWait%", CpuIowait)
    print(CDATA_INFO)
    print(arr_cdata_values)
    print("String to send to grafana:")
    print(netcat_str)

# MAIN
linux_os_srv()
