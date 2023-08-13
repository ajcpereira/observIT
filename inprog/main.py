import sys
sys.path.append("functions_core")
from functions_core.yaml_validate import read_yaml

config = read_yaml('config4.yaml')

def create_metric_ip_dicts(config):
    result_dicts = []

    for system in config.systems:
        for metric in system.config.metrics:
            for ip in system.config.ips:
                result_dict = {
                    "name": system.name,
                    "resources_types": system.resources_types,
                    **system.config.parameters.model_dump(),
                    "metric_name": metric.name,
                    "ip": ip.ip,
                }
                if ip.alias:
                    result_dict["alias"] = ip.alias

                result_dicts.append(result_dict)

    return result_dicts

result_dicts = create_metric_ip_dicts(config)

# Print the resulting dictionaries
for result_dict in result_dicts:
    print(result_dict)
    print(result_dict['poll'])




