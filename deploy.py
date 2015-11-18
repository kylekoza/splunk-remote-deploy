#!/usr/bin/env python
import paramiko

download_command = "wget -O splunkforwarder-6.3.1-f3e41e4b37b2-linux-2.6-amd64.deb 'http://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=6.3.1&product=universalforwarder&filename=splunkforwarder-6.3.1-f3e41e4b37b2-linux-2.6-amd64.deb&wget=true'"
deb_file = "splunkforwarder-6.3.1-f3e41e4b37b2-linux-2.6-amd64.deb"

DEPLOYMENT_SERVER = ""
NEW_SPLUNK_PASSWORD = ""

IP_LIST = [""]
USER = ""
PASS = ""


for ip in IP_LIST:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=USER, password=PASS)

    print "### Downloading Splunk..."
    stdin, stdout, stderr = client.exec_command(download_command)
    print stdout.read()

    print "### Installing Splunk..."
    stdin, stdout, stderr = client.exec_command('sudo dpkg -i {0}'.format(deb_file))
    stdin.write(PASS + '\n')
    stdin.flush()
    print stdout.read()

    print "### Setting Splunk to auto-start..."
    stdin, stdout, stderr = client.exec_command('sudo /opt/splunkforwarder/bin/splunk enable boot-start -user splunk --accept-license --answer-yes')
    print stdout.read()

    print "### Configuring Splunk as a deployment client..."
    stdin, stdout, stderr = client.exec_command('sudo -H -u splunk /opt/splunkforwarder/bin/splunk set deploy-poll "{0}" --accept-license --no-prompt -auth admin:changeme'.format(DEPLOYMENT_SERVER))
    print stdout.read()

    print "### Changing Splunk admin password..."
    stdin, stdout, stderr = client.exec_command('sudo -H -u splunk /opt/splunkforwarder/bin/splunk edit user admin -password {0} -auth admin:changeme'.format(NEW_SPLUNK_PASSWORD))
    print stdout.read()

    print "### Starting Splunk..."
    stdin, stdout, stderr = client.exec_command('sudo -H -u splunk /opt/splunkforwarder/bin/splunk start --accept-license --answer-yes --auto-ports --no-prompt')
    print stdout.read()

    client.close()
