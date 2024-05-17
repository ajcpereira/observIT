########################################################################################################################
#
# This stores old grafana_fun functions that created old panels
# It's just history until next version is created
# This file isn't needed, all functions will be commented
#
########################################################################################################################




# def graph_linux_os_mem(system_name, resource_name, y_pos):
#     str_title = "Memory Usage (" + resource_name + ")"
#     panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
#     pos = y_pos + 1
#
#     target_mem = [InfluxDBTarget(
#         query="SELECT  (total)-(avail) as \"Used\", (avail) as \"Available\", \"total\" as \"Total\", "
#               "\"used\"/\"total\"*100 as \"Used%\" FROM \"mem\" WHERE $timeFilter AND (\"system\"::tag = '" +
#               system_name + "') GROUP BY \"host\"::tag ORDER BY time DESC LIMIT 1",
#         format="table")]
#
#     json_overrides = [
#         {
#             "matcher": {
#                 "id": "byName",
#                 "options": "Total"
#             },
#             "properties": [
#                 {
#                     "id": "custom.hideFrom",
#                     "value": {
#                         "tooltip": False,
#                         "viz": True,
#                         "legend": True
#                     }
#                 }
#             ]
#         },
#         {
#             "matcher": {
#                 "id": "byName",
#                 "options": "Used%"
#             },
#             "properties": [
#                 {
#                     "id": "unit",
#                     "value": "percent"
#                 },
#                 {
#                     "id": "custom.hideFrom",
#                     "value": {
#                         "tooltip": False,
#                         "viz": True,
#                         "legend": True
#                     }
#                 }
#             ]
#         }
#     ]
#
#     panels_list.append(CollectorBarChart(
#         title="Memory Usage",
#         dataSource='default',
#         targets=target_mem,
#         drawStyle='line',
#         lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
#         gradientMode=COLLECTOR_GRADIENT_MODE,
#         fillOpacity=COLLECTOR_FILL_OPACITY,
#         unit="decmbytes",
#         gridPos=GridPos(h=7, w=24, x=0, y=pos),
#         spanNulls=COLLECTOR_SPAN_NULLS,
#         legendPlacement="right",
#         legendDisplayMode="table",
#         stacking={'mode': "normal"},
#         tooltipMode="multi",
#         overrides=json_overrides,
#     )
#     )
#
#     pos = pos + 7
#
#     return pos, panels_list


# def graph_linux_os_mem_old_pie(system_name, resource_name, metric, y_pos):
#     str_title = f"Memory Usage ({resource_name})"
#     panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
#     pos = y_pos + 1
#     x_pos = 0
#
#     query_template = (
#         "SELECT last(\"{field}\") FROM \"mem\" "
#         "WHERE (\"system\"::tag = '{system}' AND \"host\"::tag = '{host}') "
#         "AND $timeFilter GROUP BY time($__interval) fill(none) ORDER BY time DESC LIMIT 1"
#     )
#
#     for host in metric['hosts']:
#         target_net = [
#             InfluxDBTarget(query=query_template.format(field="avail", system=system_name, host=host), alias="Available"),
#             InfluxDBTarget(query=query_template.format(field="used", system=system_name, host=host), alias="Used"),
#         ]
#
#         panels_list.append(
#             CollectorPieChartv2(
#                 title=f"{host} Memory",
#                 dataSource='default',
#                 targets=target_net,
#                 unit=COLLECTOR_MEM_UNITS,
#                 gridPos=GridPos(h=7, w=4, x=x_pos, y=pos),
#                 legendDisplayMode="hidden",
#                 tooltipMode="multi",
#                 displayLabels=["name", "value", "percent"],
#                 pieType='donut'
#             )
#         )
#
#         x_pos += 4
#         if x_pos == 24:
#             x_pos = 0
#             pos += 7
#
#     pos += 7
#     return pos, panels_list


# def graph_linux_os_fs(system_name, resource_name, metric, y_pos):
#     str_title = f"File System Capacity ({resource_name})"
#     panels_list = [RowPanel(title=str_title, gridPos=GridPos(h=1, w=24, x=0, y=y_pos))]
#     pos = y_pos + 1
#
#     for host in metric['hosts']:
#         target_fs = [
#             InfluxDBTarget(
#                 query=f"SELECT \"used\" as \"Used\", \"total\"-\"used\" as \"Available\", \"total\" as \"Total\", \"used\"/\"total\"*100 as \"%Used\" FROM \"fs\" "
#                       f"WHERE $timeFilter AND ( \"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') "
#                       f"GROUP BY \"mount\"::tag ORDER BY time DESC LIMIT 1",
#                 format="table"
#             )
#         ]
#
#         target_fs_table = [
#             InfluxDBTarget(
#                 query=f"SELECT \"used\"/\"total\"*100 as \"%Used\", \"total\" as \"Total\", \"used\" as \"Used\", \"total\"-\"used\" as \"Available\" FROM \"fs\" "
#                       f"WHERE $timeFilter AND ( \"system\"::tag = '{system_name}' AND \"host\"::tag = '{host}') "
#                       f"GROUP BY \"mount\"::tag ORDER BY time DESC LIMIT 1",
#                 format="table"
#             )
#         ]
#
#         json_overrides = [
#             {
#                 "matcher": {
#                     "id": "byName",
#                     "options": "%Used"
#                 },
#                 "properties": [
#                     {
#                         "id": "unit",
#                         "value": "percent"
#                     },
#                     {
#                         "id": "custom.hideFrom",
#                         "value": {
#                             "legend": True,
#                             "tooltip": False,
#                             "viz": True
#                         }
#                     }
#                 ]
#             },
#             {
#                 "matcher": {
#                     "id": "byName",
#                     "options": "Total"
#                 },
#                 "properties": [
#                     {
#                         "id": "custom.hideFrom",
#                         "value": {
#                             "legend": True,
#                             "tooltip": False,
#                             "viz": True
#                         }
#                     }
#                 ]
#             },
#             {
#                 "matcher": {
#                     "id": "byName",
#                     "options": "Used"
#                 },
#                 "properties": [
#                     {
#                         "id": "thresholds",
#                         "value": {
#                             "mode": "percentage",
#                             "steps": [
#                                 {
#                                     "color": "green",
#                                     "value": None
#                                 },
#                                 {
#                                     "color": "red",
#                                     "value": 95
#                                 }
#                             ]
#                         }
#                     },
#                     {
#                         "id": "color",
#                         "value": {
#                             "mode": "thresholds"
#                         }
#                     }
#                 ]
#             }
#         ]
#
#         panels_list.append(CollectorBarChart(
#             title=host + " File System Capacity Chart",
#             dataSource='default',
#             targets=target_fs,
#             drawStyle='line',
#             lineInterpolation=COLLECTOR_LINE_INTERPOLATION,
#             gradientMode=COLLECTOR_GRADIENT_MODE,
#             fillOpacity=COLLECTOR_FILL_OPACITY,
#             unit=COLLECTOR_FS_UNITS,
#             gridPos=GridPos(h=7, w=24, x=0, y=pos),
#             spanNulls=COLLECTOR_SPAN_NULLS,
#             legendPlacement="right",
#             legendDisplayMode="table",
#             stacking={"mode": "normal", "group": "A"},
#             tooltipMode="multi",
#             xTickLabelRotation=-45,
#             valueDecimals=2,
#             overrides=json_overrides,
#             )
#         )
#
#         json_overrides_table = [
#             {
#                 "matcher": {
#                     "id": "byName",
#                     "options": "%Used"
#                 },
#                 "properties": [
#                     {
#                         "id": "unit",
#                         "value": "percent"
#                     },
#                     {
#                         "id": "custom.cellOptions",
#                         "value": {
#                             "mode": "basic",
#                             "type": "gauge",
#                             "valueDisplayMode": "color"
#                         }
#                     },
#                     {
#                         "id": "max",
#                         "value": 100
#                     },
#                     {
#                         "id": "min",
#                         "value": 0
#                     },
#                     {
#                         "id": "thresholds",
#                         "value": {
#                             "mode": "percentage",
#                             "steps": [
#                                 {
#                                     "color": "green",
#                                     "value": None
#                                 },
#                                 {
#                                     "color": "red",
#                                     "value": 95
#                                 }
#                             ]
#                         }
#                     }
#                 ]
#             },
#             {
#                 "matcher": {
#                     "id": "byName",
#                     "options": "Time"
#                 },
#                 "properties": [
#                     {
#                         "id": "custom.hidden",
#                         "value": True
#                     }
#                 ]
#             }
#         ]
#
#         table_field_sort = [TableSortByField(displayName='%Used', desc=True)]
#
#         panels_list.append(CollectorTable(
#             title=host + " File System Capacity Table",
#             dataSource='default',
#             targets=target_fs_table,
#             gridPos=GridPos(h=7, w=24, x=0, y=pos + 7),
#             filterable=True,
#             unit=COLLECTOR_FS_UNITS,
#             displayMode="color-text",
#             colorMode="thresholds",
#             overrides=json_overrides_table,
#             sortBy=table_field_sort,
#             )
#         )
#
#         pos = pos + 14
#
#     return pos, panels_list
