import time
import logging
import os


def linux_os_cpu():
    # Linux command returns cpu usage % and Iowait %
    # These are percentages of total CPU time.
    #   id: Time spent idle.  Prior to Linux 2.5.41, this includes IO-wait time.
    #   wa: Time spent waiting for IO.  Prior to Linux 2.5.41, included in idle.
    # CMD1 = "echo $[100 -$(vmstat 1 2 | tail -1 | awk '{print $15}')]"

    # Definitions/Constants
    LABEL_CPU_USAGE = "cpu_usage_percent"
    LABEL_CPU_IOWAIT = "cpu_iowait_percent"
    # These are simulated variables, must be deleted in final code
    PLATFORM = "Linux"
    PLATFORM_NAME = "CS_IDP"
    PLATFORM_TYPE = "linux-os"
    hostname = "srv01.lab.local"

    CMD1 = "echo $(vmstat 1 2 | tail -1 | awk '{print $15, $16}')"
    logging.info("%s : Starting ssh execution to get linux-os-cpu metrics", time.ctime())
    logging.debug("%s : Command Line - %s", time.ctime(), CMD1)
    print("executing command:", CMD1)
    response = os.popen(CMD1).read()
    logging.debug("%s : Output of Command Line - %s", time.ctime(), response)
    logging.info("%s : Finished ssh execution to get metrics", time.ctime())
    timestamp = int(time.time())
    print("command response (%usage %iowait):", response)

    Values = response.split()
    CpuUsage = 100 - int(Values[0])
    CpuIowait = Values[1]

    netcat_str = str(PLATFORM) + "." + str(PLATFORM_NAME) + "." + str(PLATFORM_TYPE) + "." + hostname.replace(".", "-")+"."+LABEL_CPU_USAGE + "." + str(CpuUsage) + "." + LABEL_CPU_IOWAIT + "." + CpuIowait + "." + str(timestamp) + "\n"
    logging.debug("%s : Values sent to graphana - %s", time.ctime(), netcat_str)
    print("CPU Use%", CpuUsage, "CPU IoWait%", CpuIowait)
    print(netcat_str)


linux_os_cpu()