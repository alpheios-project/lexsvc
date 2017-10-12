#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script check a list of websites
# and sends mail when the HTTP status code is not 200
#
# Used to check wheter all projects are up and running
# (not broken, say for example because a dependency library was removed)

# Author Ando Roots 2012
# Version 1.0
# Licence: Apache Licence Version 2.0
# http://sqroot.eu/2012/01/python-check-that-your-projects-are-still-alive/

import httplib
import yaml
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Holds the config options. Populated from the config file
config = None

# Is set to False when any checked sites return HTTP code other than 200
# The report mail is sent when this is False
all_valid = True

# ------------- START config

# Config filename
config_file = 'http_check.yaml'

def http_report(site, http_status,config):
    log(str(http_status)+ ","+site, config, False)

    return # Any custom actions here

# -------------- END config - do not edit below unless you know what's going on

# Read a list of sites to check
def read_config():
    global config
    f = open(config_file)
    config = yaml.load(f)
    f.close()
    return config

def read_index_file(file):
    entries = []
    f = open(file)
    for line in f:
        lemma,id = line.rstrip().split('|')
        entries.append(id)
    return entries

# Function from http://stackoverflow.com/a/1140822/401554
# Get HTTP status code of a domain + path
def get_status_code(host, path="/", https = False):
    """ This function retreives the status code of a website by requesting
        HEAD data from the host. This means that it only requests the headers.
        If the host cannot be reached or something else goes wrong, it returns
        None instead.
    """
    try:
        if (https):
            conn = httplib.HTTPSConnection(host)
        else:
	    conn = httplib.HTTPConnection(host)
        conn.request("GET", path)
        return conn.getresponse().status
    except StandardError:
        return None


# Main - read config, check each site
def main():
    global all_valid, config

    # Contains a list of sites to check
    config = read_config()

    log(str(datetime.now())+': Starting check.',config,True)

    # check each index
    for file in config['files']:
        ids = read_index_file(file['path'])
        # Check each site
        for site in config['sites']:
            uri = "/"+site['uri']
            uri = uri.replace('<LEX>',file['lex'])
            uri = uri.replace('<LANG>',file['lang'])
            if ('https' in site):
                https = True
            else:
                https = False
            for id in ids:
                test_uri = uri.replace('<LEMMAID>',id)
                # Get the HTTP code
                code = get_status_code(site['domain'], uri, https)
                checked = site['domain'] + test_uri
                print("Checking "+site['name']+" ("+checked+") ... "+ str(code),config)

                http_report(checked, code, config)
                if (code != 200):
                    all_valid = False

    log(str(datetime.now())+': Checking completed. All valid: ' + str(all_valid),config,False)

    # Send report when failures need reporting
    if (not all_valid):
        print('Some sites failed.',config)
    else:
        print('All tests reported status code 200.',config)


def log(string,config,newlog=False):
    string = string + "\n"
    print string

    # Log results to a file
    if (config['log']):

        try:
	        # Console output file
            if newlog:
                mode = 'w'
            else:
                mode = 'a'
            f = open(config['output_file'], mode)
            f.write(string)
            f.close()
        except Exception:
	        print 'Error writing output buffer file'


# Call the main function
main()
