SHELL := /bin/bash
LOG_PATH := $(PWD)/log


.PHONY: default
default: usage ;
usage:
	@echo "Usage:"
	@echo "make install"
	@echo "make start"
	@echo "make stop"
	@echo "make remove"
	
.ONESHELL:
setup:
	
	mkdir -p /opt/fj-collector/graphite/data/storage
	mkdir -p /opt/fj-collector/graphite/data/statsd_config
	mkdir -p /opt/fj-collector/graphite/data/conf
	mkdir -p /opt/fj-collector/grafana/provisioning
	mkdir -p /opt/fj-collector/grafana/data/grafana
	mkdir -p /opt/fj-collector/collector/logs
	mkdir -p /opt/fj-collector/collector/config
	mkdir -p /opt/fj-collector/collector/keys

	cp ./install/Dockerfile .
	podman build . -t fj-collector:latest

	podman pull docker.io/graphiteapp/graphite-statsd
	podman pull docker.io/grafana/grafana-enterprise

	cp config/config.yaml /opt/fj-collector/collector/config

	podman run -d \
 	--name graphite \
 	--restart=always \
 	-p 80:80/tcp \
	-p 12003:2003/tcp \
	-p 18125:8125/udp \
	-v /etc/localtime:/etc/localtime:ro \
	-v /opt/fj-collector/graphite/data/conf:/opt/graphite/conf \
	-v /opt/fj-collector/graphite/data/storage:/opt/graphite/storage \
	-v /opt/fj-collector/graphite/data/statsd_config:/opt/statsd/config \
	--log-opt max-size=10m --log-opt max-file=3 \
	graphiteapp/graphite-statsd
	
	podman run -d \
	--name grafana \
    --restart=always \
    -p 3000:3000/tcp \
    -v /opt/fj-collector/grafana/provisioning/:/etc/grafana/provisioning/ \
    -v /opt/fj-collector/grafana/data/grafana:/var/lib/grafana/ \
    -u 0 \
	--log-opt max-size=10m --log-opt max-file=3 \
	grafana/grafana-enterprise
	
	podman run -d \
	--name fj-collector \
	--restart=always \
	-v /opt/fj-collector/collector/logs:/collector/logs \
	-v /opt/fj-collector/collector/config:/collector/config \
	-v /opt/fj-collector/collector/keys:/collector/keys \
	--log-opt max-size=10m --log-opt max-file=3 \
	localhost/fj-collector:latest

	rm Dockerfile 

.ONESHELL:
stop:
	podman stop graphite
	podman stop grafana
	podman stop fj-collector

.ONESHELL:
remove:
	podman rm graphite
	podman image rm docker.io/graphiteapp/graphite-statsd
	podman rm grafana
	podman image rm docker.io/grafana/grafana-enterprise
	podman rm fj-collector
	podman image rm localhost/fj-collector
	podman image rm docker.io/library/debian

.ONESHELL:
start:
	podman start graphite
	podman start grafana
	podman start fj-collector
	podman inspect grafana -f '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'
	podman inspect graphite -f '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'
	podman inspect fj-collector -f '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'