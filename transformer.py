#!  /usr/bin/python

import re
import sys


def detect_prompts ( interact_output ):
    prompt_pattern_list = []
    prompt_pattern = re.compile("ERROR:Session:INPUT:>:(.*?)\nERROR:Session:OUTPUT:>(.*?)\n", re.DOTALL|re.MULTILINE)
    for pattern in prompt_pattern.findall(interact_output):
        (cmd,out)=pattern
        result = re.match(("(.*)%s$"%cmd),out)
        prompt_pattern_list.append(result.group(1))
        prompt_set = set(prompt_pattern_list)
    return prompt_set

def transform (interact_output):

    regex = re.compile("^ERROR:Session:INPUT:>:(.*?)\n", re.DOTALL|re.MULTILINE)

    output = regex.sub(r'session.execute("\1")\n',interact_output)
    return output


interact_output = open(sys.argv[1]).read()
transformed_file = open(sys.argv[2],"w")

prompt_set = detect_prompts (interact_output)
print (len(prompt_set), prompt_set)

transformed_file.write(transform(interact_output))

