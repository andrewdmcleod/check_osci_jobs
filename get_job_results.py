#!/usr/bin/python3

# Script fetches mojospec results from osci and dumps to 2 json files

import urllib.request, json , os, time, keyboard, sys, re, operator
from collections import OrderedDict
import time
import copy
import pprint

os.environ['http_proxy'] = ''

numBuilds = 100

all_urls = { 'charm_pusher': "http://osci:8080/view/CS/",
	     'mojo_matrix': "http://osci:8080/view/MojoMatrix/"
}

count = 1 
matrix = {}
matrix_full = {}
matrix_last = {}
addrow = False
configs = {}
configss = {}
first_run = 0 
out_lines = {}

for cur_url in all_urls.items():
    first_run = 0 
    output_filename = "{}_failures.txt".format(cur_url[0])
    try:
        with open(output_filename, "r") as check_file:
            #print ("file opened")
            pass
    except FileNotFoundError as fnf:
            #print ("File not found, first run, just adding things without alerting")
            first_run = 1
            with open(output_filename, "w") as create_file:
                create_file.write("{}")
    #print (cur_url)
    configss = {}
    matrix = {}
    #print(cur_url[1])
    with urllib.request.urlopen("{}/api/json/".format(cur_url[1])) as jsonurl:
        jsdata = json.loads(jsonurl.read().decode())
        #pprint.pprint(jsdata['jobs'])
        with open(output_filename, "r") as read_file:
            in_lines = json.loads(read_file.read())
            #print(type(in_lines))
            for job in jsdata['jobs']:
                url = job['url']
                color = job['color']
                name = job['name']
                if color == "red": 
                    try:
                        with urllib.request.urlopen("{}/lastBuild/api/json/".format(url)) as job_jsonurl:
                            js_job_data = json.loads(job_jsonurl.read().decode())
                            #print ("Failed ({}): {}{}/consoleFull".format(color, url, js_job_data['id']))
                            if first_run == 1:
                                out_lines[url] = js_job_data['id']
                                line_scan = "{}{}".format(url, js_job_data['id'])
                            else:
                                for ex_url, ex_id in in_lines.items():
                                    #print("Looking for {} in {} ... and {} in {}".format(url, ex_url, js_job_data['id'], ex_id))
                                    if ex_url == url:
                                        if js_job_data['id'] == ex_id:
                                            #print("already alerted ---------------------------------- {}".format(ex_url)) 
                                            out_lines[ex_url] = ex_id
                                        else:
                                            print("{} job failed ({}) -- {}{}/consoleFull".format(name, color, url, js_job_data['id']))
                                            out_lines[ex_url] = js_job_data['id']
                    except urllib.error.HTTPError as e:
                        pass
        with open(output_filename, "w") as write_file:
            #if in_lines == out_lines: print ("no change")
            #print("------------------------------------")
            #print(in_lines)
            #print("------------------------------------")
            #print(out_lines)
            #print("------------------------------------")
            write_file.write(json.dumps(out_lines))
