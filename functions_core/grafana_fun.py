
from grafanalib.core import *
from grafanalib._gen import DashboardEncoder
import json, requests
from functions_core.yaml_validate import *


def cp_linux_os_srv_cpu_load(**kwargs):
    str_cpu_load = "aliasByNode(tst-collector" + "." + kwargs['name'] + "." + kwargs[
        'resources_types'] + ".*.cpu.load5m, 3)"

    timeseries_panel = TimeSeries(
        title="CPU load (5m)",
        dataSource='default',
        targets=[
            Target(
                datasource='default',
                expr=str_cpu_load,
                target=str_cpu_load,
            ),
        ],
        drawStyle='line',
        lineInterpolation='smooth',
        gradientMode='hue',
        fillOpacity=25,
        gridPos=GridPos(h=7, w=12, x=12, y=2),
    )

    print(timeseries_panel)
    return timeseries_panel


def panel_linux_os_cpu(**kwargs):
    data = []

    for host in kwargs:
        str_cpu_use = "aliasByNode(" + kwargs['collector'] + ".cpu.use, 3)"
        data = data.append("Target(datasource='default', expr=" + str_cpu_use + ", target=" + str_cpu_use + "),")

    timeseries_panel = TimeSeries(
        title="CPU utilization (%)",
        dataSource='default',
        targets=data,
        drawStyle='line',
        lineInterpolation='smooth',
        gradientMode='hue',
        fillOpacity=25,
        gridPos=GridPos(h=7, w=12, x=0, y=2),
    )
    print(timeseries_panel)

    return timeseries_panel


def get_dashboard_json(dashboard, overwrite=False, message="Updated by grafanlib"):
    '''
    get_dashboard_json generates JSON from grafanalib Dashboard object

    :param dashboard - Dashboard() created via grafanalib
    '''

    # grafanalib generates json which need to pack to "dashboard" root element
    return json.dumps(
        {
            "dashboard": dashboard.to_json_data(),
            "overwrite": overwrite,
            "message": message
        }, sort_keys=True, indent=2, cls=DashboardEncoder)


def upload_to_grafana(json, server, api_key, verify=True):
    '''
    upload_to_grafana tries to upload dashboard to grafana and prints response

    :param json - dashboard json generated by grafanalib
    :param server - grafana server name
    :param api_key - grafana api key with read and write privileges
    '''

    headers = {'Authorization': f"Bearer {api_key}", 'Content-Type': 'application/json'}

    try:
        r = requests.post(f"http://{server}/api/dashboards/db", data=json, headers=headers, verify=verify)
    except:
        logging.error("Unable to create dashboard in grafana!" )
        #print(f"{r.status_code} - {r.content}")



def create_timeseries_panel(str_title, panels_list, obj_grid_pos, unit):

    timeseries_panel = TimeSeries(
        title=str_title,
        dataSource='default',
        targets=panels_list,
        drawStyle='line',
        lineInterpolation='smooth',
        gradientMode='hue',
        fillOpacity=25,
        unit=unit,
        gridPos=obj_grid_pos,
    )

    return timeseries_panel


def create_stat_panel(str_title, panels_list, obj_grid_pos, unit):

    stat_panel = Stat(
        title=str_title,
        dataSource='default',
        targets=panels_list,
        gridPos=obj_grid_pos,
        #unit=unit,
    )

    return stat_panel


def create_bargauge_panel(str_title, panels_list, obj_grid_pos, unit):

    #falta actualizar as propriedades de acordo com o json gravado no desktop


    tst = {"fieldConfig": {"overrides": [{"matcher": {"id": "byName","options": "Value"},"properties": [{"id": "max"}]}]}}
    #tst = {"fieldConfig": {"defaults": {"color": {"mode": "palette-classic"}}}, "overrides": [{"matcher": {"id": "byName","options": "Value"},"properties": [{"id": "max"}]}]}
    print(tst)

    #tst = {"fieldConfig": {"defaults": {"color": {"mode": "palette-classic"}}},}

    bargauge_panel = BarGauge(
        title=str_title,
        dataSource='default',
        targets=panels_list,
        orientation='vertical',
        displayMode='basic',
        calc='lastNotNull',
        format=unit,
        gridPos=obj_grid_pos,
        min=0,
        extraJson=tst,
    )
    print(bargauge_panel.to_json_data())

    return bargauge_panel



def create_panel_linux_os(system_name, resource_name, data):

    panels_list =[]
    begin_str = "tst-collector." + system_name + "." + resource_name + "."

    for metric in data:

        match metric['metric']:
            case "cpu":
                panels_target_list_cpu_use = []
                panels_target_list_cpu_load = []
                panels_list.append(RowPanel(title=resource_name + ': CPU', gridPos=GridPos(h=1, w=24, x=0, y=1)))
                for host in metric['hosts']:
                    str_cpu_use = "aliasByNode(" + begin_str + host + ".cpu.use, 3)"
                    str_cpu_load = "aliasByNode(" + begin_str + host + ".cpu.load5m, 3)"
                    panels_target_list_cpu_use.append(Target(datasource='default', expr=str_cpu_use, target=str_cpu_use))
                    panels_target_list_cpu_load.append(Target(datasource='default', expr=str_cpu_load, target=str_cpu_load))
                panels_list.append(
                    create_timeseries_panel("CPU utilization (%)", panels_target_list_cpu_use, GridPos(h=7, w=12, x=0, y=1), ""))
                panels_list.append(
                    create_timeseries_panel("CPU Load 5 min", panels_target_list_cpu_load, GridPos(h=7, w=12, x=12, y=1), ""))
            case "mem":
                panels_list.append(RowPanel(title=resource_name + ': Memory', gridPos=GridPos(h=1, w=24, x=0, y=2)))
                xpos = 0
                for host in metric['hosts']:
                    panels_target_list_mem = []
                    str_mem_total = "aliasByNode(" + begin_str + host + ".mem.total, 5)"
                    str_mem_used = "aliasByNode(" + begin_str + host + ".mem.used, 5)"
                    panels_target_list_mem.append(Target(datasource='default', expr=str_mem_total, target=str_mem_total))
                    panels_target_list_mem.append(Target(datasource='default', expr=str_mem_used, target=str_mem_used))
                    panels_list.append(create_bargauge_panel(host + " Memory Usage", panels_target_list_mem,GridPos(h=7, w=3, x=xpos, y=2), unit="decmbytes"))
                    xpos=xpos+6
            case "net":
                panels_list.append(RowPanel(title=resource_name + ': Network', gridPos=GridPos(h=1, w=24, x=0, y=4)))
                for host in metric['hosts']:
                    str_net_rx = "aliasByNode(derivative(" + begin_str + host + ".net.*.rx_mbp), 3, 5)"
                    str_net_tx = "aliasByNode(derivative(" + begin_str + host + ".net.*.tx_mbp), 3, 5)"
                    tgt_net_rx = [Target(datasource='default', expr=str_net_tx, target=str_net_tx)]
                    tgt_net_tx = [Target(datasource='default', expr=str_net_rx, target=str_net_rx)]
                    panels_list.append(create_timeseries_panel(host + " Network Outbound", tgt_net_tx, GridPos(h=7, w=12, x=0, y=4), "MBs"))
                    panels_list.append(create_timeseries_panel(host + " Network Inbound", tgt_net_rx, GridPos(h=7, w=12, x=12, y=4), "MBs"))
            case "fs":
                panels_list.append(RowPanel(title=resource_name + ': File System', gridPos=GridPos(h=1, w=24, x=0, y=3)))
                for host in metric['hosts']:
                    str_fs_used = "aliasByNode(aliasSub(" + begin_str + host + ".fs.*.used, '_dash_', '/'), 5, 6)"
                    str_fs_total = "aliasByNode(aliasSub(" + begin_str + host + ".fs.*.total, '_dash_', '/'), 5, 6)"
                    tgt_fs_used = [Target(datasource='default', expr=str_fs_used, target=str_fs_used)]
                    tgt_fs_total = [Target(datasource='default', expr=str_fs_total, target=str_fs_total)]
                    panels_list.append(
                        #create_timeseries_panel(host + " Filesystem", tgt_fs_used + tgt_fs_total, GridPos(h=7, w=24, x=0, y=3), "decgbytes"))
                        create_bargauge_panel(host + " Filesystem", tgt_fs_used + tgt_fs_total,GridPos(h=7, w=24, x=0, y=3), "decgbytes"))

    return panels_list


def create_system_dashboard(sys):

    panels=[]

    for res in sys['resources']:
        match res['name']:
            case "linux_os":
                panels = panels + create_panel_linux_os(str(sys['system']), str(res['name']), res['data'])
            case "eternus_icp":
                print(res['name'])

    my_dashboard = Dashboard(
        title="System " + sys['system'] + " dashboard",
        description="fj-collector auto generated dashboard",
        tags=[
            sys['system'],
        ],
        timezone="browser",
        panels=panels,

     ).auto_panel_ids()


    return my_dashboard



def build_dashboards(systems):

    grafana_api_key = "glsa_HpGYv397ImTmgMyg2z3K76dvtCLfbTVz_6baa303d"
    grafana_server = "localhost:3000"

    for sys in systems:
        print("create_system_dash(sys)", sys['system'])
        my_dashboard = create_system_dashboard(sys)
        my_dashboard_json = get_dashboard_json(my_dashboard, overwrite=True)
        print(my_dashboard_json)
        upload_to_grafana(my_dashboard_json, grafana_server, grafana_api_key)


def build_grafana_fun_data_model(config):

    def check_if_metric_exists(system_name, resource_name, metric_name, lst):
        metrics_lst = []
        b_exists = False

        for x in lst:
            #print(x['system'])
            if system_name in x['system']:
                #print("system:", system_name, " found!!")
                for y in x['resources']:
                    #print("resource name xxxxx", y)
                    if resource_name in y['name']:
                        #print("resource: ", y['name'], "found")
                        for z in y['data']:
                            if metric_name in z['metric']:
                                #print("metric: ", z['metric'], "found")
                                metrics_lst = z['hosts']
                                b_exists = True
                                #print(z)

        #print(metrics_lst)

        return b_exists, metrics_lst

    def check_if_system_exists(system_name, lst):

        b_result = False
        for x in lst:
            #print(x['system'])
            if system_name in x['system']:
                b_result = True

        return b_result

    def check_if_resource_exists(system_name, resource_name, lst):

        resource_lst = []
        b_result = False

        for x in lst:
            if system_name in x:
                for y in x['resources']:
                    if resource_name in y['name']:
                        #resource_lst = y
                        b_result = True

        return b_result

    def my_update_resource_list(system_name, resource_name, metric_name, lst, dict_metric):
        metrics_lst = []
        b_exists = False

        for x in lst:
            if system_name in x['system']:
                for y in x['resources']:
                    if resource_name in y['name']:
                        for z in y['name']:
                            for k in y['data']:
                                if metric_name in k['metric']:
                                    k.update(dict_metric)

        return lst


    def add_resource(system_name, dict, model):

        local_model = model

        for x in local_model:
            if system_name in x['system']:
                x['resources'].append(dict)
                #print("existing resources", x)

        #print("local model", local_model)
        return local_model


    model_result = []
    for system in config.systems:
        metric_list = []
        res_list = []
        for metric in system.config.metrics:
            host_list = []
            #print("model result", model_result)
            for ip in system.config.ips:
                host_list.append(ip.alias)
            met_exists, met_hosts_lst = check_if_metric_exists(system.name, system.resources_types, metric.name, model_result)
            #print("existing", metric.name, met_hosts_lst, met_exists)
            #print("new", metric.name, host_list)
            if met_exists:
                metric_dict = {'metric': metric.name, 'hosts': met_hosts_lst + host_list}
                model_result = my_update_resource_list(system.name, system.resources_types, metric.name, model_result, metric_dict)
            else:
                metric_list.append({'metric': metric.name, 'hosts': host_list})
            #print("metric_list:", met_exists, metric_list)
        res_exists = check_if_resource_exists(system.name, system.resources_types, model_result)
        if (not res_exists):
            #print("resource do not exists but system exists")
            res_list.append({'name':system.resources_types, 'data': metric_list})
        if check_if_system_exists(system.name, model_result):
            #print("o sistema existe", model_result)
            model_result = add_resource(system.name, {'name':system.resources_types, 'data': metric_list}, model_result)
        else:
            model_result.append({'system':system.name, 'resources':res_list})

    return model_result


def run():


    kwargs = {'name': 'MYCS8000',
              'resources_types': 'linux_os',
              'user': 'super',
              'host_keys': 'keys/id_rsa',
              'poll': 1,
              'use_sudo': True,
              'snmp_community': None,
              'bastion': None,
              'ism_server': None,
              'ism_password': None,
              'ism_port': None,
              'ism_secure': True,
              'metric_name': 'cpu',
              'ip': '127.0.0.1',
              'alias': 'linux01',
              'ip_snmp_community': None,
              'ip_use_sudo': False,
              'ip_host_keys': None,
              'ip_bastion': None,
              'func': 'linux_os_srv',
              'repository': '10.88.0.4',
              'repository_port': 2003,
              'repository_protocol': 'tcp',
              'loglevel': 'DEBUG',
              'logfile': 'logs/fj-collector.log'
              }

    configfile_default = "/home/super/fj-collector/inprog/config/config.yaml"
    config, orig_mtime, configfile_running = configfile_read(sys.argv, configfile_default)

    #print(config)
    #print(yaml.dump(config))
    #exit(1)
    model_result = build_grafana_fun_data_model(config)
    print(model_result)
    build_dashboards(model_result)



run()
