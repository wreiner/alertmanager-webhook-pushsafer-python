import json
import sys
import logging

from dateutil import parser
from flask import Flask
from flask import request
from flask_basicauth import BasicAuth

from pushsafer import init, Client


# global variables
conf_data = None
conf_file = "/etc/pushsafer_alertmanager_webhook.conf"
app = Flask(__name__)

localinit()

def fatal_end(msg):
    print(msg)
    sys.exit(1)

def localinit():
    json_data = open(conf_file).read()
    conf_data = json.loads(json_data)

    app.secret_key = conf_data.get("secret_key", None)
    if app.secret_key is None:
        fatal_end("no secret_key supplied")

    # enable and configure basic authentication
    basic_auth = BasicAuth(app)
    app.config['BASIC_AUTH_FORCE'] = True
    app.config['BASIC_AUTH_USERNAME'] = conf_data.get("basic_auth_username", "changeme")
    app.config['BASIC_AUTH_PASSWORD'] = conf_data.get("basic_auth_password", "changeme")
    print(app.config['BASIC_AUTH_USERNAME'])
    print(app.config['BASIC_AUTH_PASSWORD'])
    print(app.secret_key)

def apush_notification(subject, message):
    print(subject)
    print(message)

def push_notification(push_subject, message):
    init(conf_data["pushsafer_privatekey"])

    body_text = message
    icon = 5
    sound = 61
    vibration = 3
    url = ""
    url_title = ""
    time2live = 0
    priority = 2
    retry = 0
    expire = 0
    answer = 0
    image_1 = ""
    image_2 = ""
    image_3 = ""

    # send_message fields:
    Client("").send_message(
            body_text,
            push_subject,
            conf_data["pushsafer_device_or_group"],
            icon,
            sound,
            vibration,
            url,
            url_title,
            time2live,
            priority,
            retry,
            expire,
            answer,
            image_1,
            image_2,
            image_3)

@app.route('/alert', methods = ['POST'])
def postAlertmanager():
    print("in postAlertmanager")
    try:
        content = json.loads(request.get_data())
        print(content)
        for alert in content['alerts']:
            # build subject first
            subject = ""

            if "severity" in alert["labels"]:
                subject = "[{}]".format(alert["labels"]["severity"])

            if "instance" in alert["labels"]:
                subject = "{} {}".format(subject, alert["labels"]["instance"])

            if "alertname" in alert["labels"]:
                subject = "{} {}".format(subject, alert["labels"]["alertname"])

            message = "Status: "+alert['status']+"\n"
            if 'name' in alert['labels']:
                message += "Instance: "+alert['labels']['instance']+"("+alert['labels']['name']+")\n"
            else:
                message += "Instance: "+alert['labels']['instance']+"\n"
            if 'info' in alert['annotations']:
                message += "Info: "+alert['annotations']['info']+"\n"
            if 'summary' in alert['annotations']:
                message += "Summary: "+alert['annotations']['summary']+"\n"
            if 'description' in alert['annotations']:
                message += "Description: "+alert['annotations']['description']+"\n"
            if alert['status'] == "resolved":
                correctDate = parser.parse(alert['endsAt']).strftime('%Y-%m-%d %H:%M:%S')
                message += "Resolved: "+correctDate
            elif alert['status'] == "firing":
                correctDate = parser.parse(alert['startsAt']).strftime('%Y-%m-%d %H:%M:%S')
                message += "Started: "+correctDate
            push_notification(subject, message)
        return "Alert OK", 200
    except RetryAfter:
        sleep(30)
        push_notification(subject, message)
        return "Alert OK", 200
    except TimedOut as e:
        sleep(60)
        push_notification(subject, message)
        return "Alert OK", 200
    except NetworkError as e:
        sleep(60)
        push_notification(subject, message)
        return "Alert OK", 200
    except Exception as error:
        push_notification(subject, message)
        app.logger.info("\t%s",error)
        return "Alert fail", 200

# main is only run in dev stage
if __name__ == '__main__':
    dev_listen_address = conf_data.get("dev_listen_address", "0.0.0.0")
    dev_listen_port = conf_data.get("dev_port", "9196")

    logging.basicConfig(level=logging.INFO)
    app.run(host=dev_listen_address, port=dev_listen_port)
