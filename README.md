# Alertmanager webhook for Pushsafer (Python Version)

A webhook for Prometheus' Alertmanager to push alerts to pushsafer written in Python.


## Alertmanager configuration example

```
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'pushsafer-webhook'
receivers:
- name: 'pushsafer-webhook'
  webhook_configs:
  - url: http://<host-or-ip>:9196/alert
    send_resolved: true
    http_config:
      basic_auth:
        username: 'user'
        password: 'password'
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']

```

## Running on docker

```
docker run --name amwh \
	-p 9196:9196 \
	-v /etc/pushsafer_alertmanager_webhook.conf:/etc/pushsafer_alertmanager_webhook.conf \
	wreiner/alertmanager-webhook-pushsafer
```

## Development

### Install

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Run development

```
source env/bin/activate
python3 pushsafer_alertmanager_webhook.py
```

### Example to test

```
curl -XPOST --data '{"status":"resolved","groupLabels":{"alertname":"instance_down"},"commonAnnotations":{"description":"i-0d7188fkl90bac100 of job ec2-sp-node_exporter has been down for more than 2 minutes.","summary":"Instance i-0d7188fkl90bac100 down"},"alerts":[{"status":"resolved","labels":{"name":"olokinho01-prod","instance":"i-0d7188fkl90bac100","job":"ec2-sp-node_exporter","alertname":"instance_down","os":"linux","severity":"page"},"endsAt":"2019-07-01T16:16:19.376244942-03:00","generatorURL":"http://pmts.io:9090","startsAt":"2019-07-01T16:02:19.376245319-03:00","annotations":{"description":"i-0d7188fkl90bac100 of job ec2-sp-node_exporter has been down for more than 2 minutes.","summary":"Instance i-0d7188fkl90bac100 down"}}],"version":"4","receiver":"infra-alert","externalURL":"http://alm.io:9093","commonLabels":{"name":"olokinho01-prod","instance":"i-0d7188fkl90bac100","job":"ec2-sp-node_exporter","alertname":"instance_down","os":"linux","severity":"page"}}' http://username:password@<host-or-ip>:9196/alert
```

## Source

* based upon [nopp/alertmanager-webhook-telegram-python](https://github.com/nopp/alertmanager-webhook-telegram-python)