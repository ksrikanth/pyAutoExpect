#!/usr/bin/python

import sys

import pexpect
import re

log_file=sys.argv[1]

def parse_iolog (filename):
    log_file = open(filename).read()
    program_re = re.compile("<program>(.*)</program>", re.DOTALL | re.MULTILINE)
    program_re_match =  program_re.match(log_file)
    program = program_re_match.group(1)

    io_re = re.compile(r"<input>\n(.*?)\n</input>\n<output>\n(.*?)\n</output>",
        re.DOTALL|re.MULTILINE)
    io_pairs = io_re.findall(log_file)

    for (cmd,response) in io_pairs:
        if ((cmd.strip() == "") and (response.strip() == "")):
            continue
    return (program,io_pairs)

def playback_cmd(program, cmd_response_list):
    process = pexpect.spawn(program)
    #process.logfile = sys.stdout
    for (cmd,response) in cmd_response_list:
        #print ("Processing...%s:%s"%(cmd, response))
        process.sendline(cmd)
        process.timeout=2
        process.expect_exact(response)
        print process.before


(program, cmd_response_list) = parse_iolog(log_file)
playback_cmd(program, cmd_response_list)

