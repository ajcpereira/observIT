import sys
sys.path.append("functions_core")
from functions_core.yaml_validate import read_yaml, AllowedMetrics

config = read_yaml('config/config4.yaml')

def create_metric_ip_dicts(config):
    result_dicts = []

    for system in config.systems:
        for metric in system.config.metrics:
            for ip in system.config.ips:
                ip_dict = vars(ip)  # Convert ip object to a dictionary
                result_dict = {
                    "name": system.name,
                    "resources_types": system.resources_types,
                    **system.config.parameters.model_dump(),
                    "metric_name": metric.name,
                    "ip": ip.ip,
                    **ip_dict,  # Include all attributes from ip object
                    "func": AllowedMetrics.get_metric_value(system.resources_types, metric.name)
                }
                result_dicts.append(result_dict)

    return result_dicts

result_dicts = create_metric_ip_dicts(config)

# Print the resulting dictionaries
for result_dict in result_dicts:
    print(result_dict)