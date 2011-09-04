#!/usr/bin/python

import sys

import pexpect
import re

import logging

class LogStringStream:
    def __init__(self, name, logger, delimitter="\r\n",init_input=""):
        self.name=name
        self.incomplete_line=init_input
        self.logger=logger
        self.delimitter=delimitter

    def add_input( self, partial_input ):
        lines = []
        #lines = splitlines(incomplete_line+partial_input)
        if partial_input.endswith(self.delimitter):
           lines = ("%s%s"%(self.incomplete_line,partial_input)).splitlines()
           self.incomplete_line = ""
        elif (partial_input.find(self.delimitter) != -1):
           lines = partial_input.splitlines()
           lines [0] = ("%s%s"%(self.incomplete_line,lines[0]))
           self.incomplete_line = lines[-1] 
           lines = lines [0:-1]
        else:
            self.incomplete_line = ("%s%s"%(self.incomplete_line,partial_input))
        return lines

    def log (self,line):
        #for line in self.add_input(partial_input):
        #self.logger.error ("%s: %s"%(self.name, line))
        if (self.log_mode == "RAW"):
            print >>self.logger, line
        else:
            self.logger.error ("%s: %s"%(self.name, line))
            

class SessionStream:
    def __init__(self,logger):
        self.in_stream = LogStringStream("INPUT:>",logger,delimitter="\r")
        self.out_stream = LogStringStream("OUTPUT:>",logger)
        self.prompts = set([])

    def in_log(self,partial_input):
        if (self.in_stream.incomplete_line == ""):
            self.prompts.add(self.out_stream.incomplete_line)
       
        lines=self.in_stream.add_input(partial_input)
        if (lines != []):
            self.in_stream.log("<input>")
            for line in lines:
                self.in_stream.log(line)
            self.in_stream.log("</input>")

    def out_log(self,partial_input):
        lines=self.out_stream.add_input(partial_input)
        if (lines != []):
            self.in_stream.log("<output>")
            for line in lines:
                self.out_stream.log(line)
            self.in_stream.log("</output>")

    def set_logmode ( self, mode):
        self.in_stream.log_mode=mode
        self.out_stream.log_mode=mode

def log_input(input_string):
    global session_stream
    session_stream.in_log(input_string)
    return input_string


def log_output(output_string):
    global session_stream
    session_stream.out_log(output_string)
    return output_string
'''
for char in "Hello\r\n":
    print ("Processing", char)
    #log_output ("%c"%char)
    log_input ("%c"%char)


'''
program = sys.argv[1]
log_file=open(sys.argv[2],"w")

#logger = logging.getLogger("Session")
#logging.basicConfig(filename="Session.log", level=logging.DEBUG)
#logger.error ("Spawning program:%s"%program)

#session_stream = SessionStream(logger)
session_stream = SessionStream(log_file)
progInstance = pexpect.spawn(program)

progInstance.timeout=2
progInstance.expect(pexpect.TIMEOUT)

session_stream.set_logmode("RAW")

#progInstance.interact(input_filter=log_input, output_filter=log_output)
progInstance.interact(input_filter=log_input, output_filter=log_output)

for prompt in sorted(session_stream.prompts):
    print "Prompts...",prompt
progInstance.close()
