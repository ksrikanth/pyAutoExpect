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
        self.logger.error ("%s: %s"%(self.name, line))
            

class SessionStream:
    def __init__(self,logger):
        self.in_stream = LogStringStream("INPUT:>",logger,delimitter="\r")
        self.out_stream = LogStringStream("OUTPUT:>",logger)
        self.prompts = set([])

    def in_log(self,partial_input):
        lines=self.in_stream.add_input(partial_input)
        if (len(lines) != 0):
            if (lines[0] != ""):
                print ("Line..%s, IncompleteLine:%s"%(lines[0],self.out_stream.incomplete_line))
                prompt_re=re.match(("(.*)%s"%lines[0]), self.out_stream.incomplete_line)
                self.prompts.add(prompt_re.group(1))
            else:
                self.prompts.add(self.out_stream.incomplete_line)
                print ("Line..", lines[0])
                print ("Incomplete_line..", self.out_stream.incomplete_line)
        for line in lines:
            self.in_stream.log(line)

    def out_log(self,partial_input):
        lines=self.out_stream.add_input(partial_input)
        for line in lines:
            self.out_stream.log(line)

program = sys.argv[1]

logger = logging.getLogger("Session")
logging.basicConfig(filename="Session.log", level=logging.DEBUG)
logger.error ("Spawning program:%s"%program)

session_stream = SessionStream(logger)

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
progInstance = pexpect.spawn(program)

progInstance.timeout=2
progInstance.expect(pexpect.TIMEOUT)
#progInstance.interact(input_filter=log_input, output_filter=log_output)
progInstance.interact(input_filter=log_input, output_filter=log_output)

for prompt in sorted(session_stream.prompts):
    print "Prompts...",prompt
progInstance.close()
