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
import urllib
import yaml
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Holds the config options. Populated from the config file
config = None

# Is set to False when any checked sites return HTTP code other than 200
# The report mail is sent when this is False
all_valid = True
all_found = True

# ------------- START config

# Config filename
config_file = 'config.yaml'

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
        lemma = line.rstrip()
        entries.append(lemma)
    return entries

def get_response(host, path="/", https = False):
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
        return conn.getresponse()
    except StandardError:
        return None


# Main - read config, check each site
def main():
    global all_valid, config, all_found

    # Contains a list of sites to check
    config = read_config()

    log(str(datetime.now())+': Starting check.',config,True)

    # check each index
    for file in config['files']:
        lemmas = read_index_file(file['path'])
        # Check each site
        for site in config['sites']:
            uri = "/"+site['uri']
            uri = uri.replace('<LEX>',file['lex'])
            uri = uri.replace('<LANG>',file['lang'])
            if ('https' in site):
                https = True
            else:
                https = False
            for lemma in lemmas:
                test_uri = uri.replace('<LEMMA>',urllib.quote_plus(lemma))
                # Get the HTTP code
                response = get_response(site['domain'], test_uri, https)
                code = response.status
                checked = site['domain'] + test_uri
                print("Checking "+site['name']+" ("+checked+") ... "+ str(code))

                http_report(checked, code, config)
                if (code != 200):
                    all_valid = False
                else:
                    data = response.read()
                    pattern = re.compile('lemma-id=[\'"](.*?)[\'"]',re.M)
                    m = pattern.search(data,re.M)
                    if m is None:
                        all_found = False
                        print("No entries found for "+site['name']+" "+checked)
                        log("---," + checked, config, False)
                    else:
			log(lemma + "=" + m.group(1), config, False)
                    

    log(str(datetime.now())+': Checking completed. All valid: ' + str(all_valid) + " All found: " + str(all_found),config,False)

    # Send report when failures need reporting
    if (not all_valid):
        print('Some lookups errored.')
    else:
        print('All tests reported status code 200.')
    if (not all_found):
        print('Some lookups failed.',config)
    else:
        print('All tests found entries.')



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
