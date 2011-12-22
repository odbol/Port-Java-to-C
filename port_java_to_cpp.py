#!/bin/python
instructions = """
This script takes an Java file and auto-ports it to C++. Well, the obvious boring stuff anyway:
It will replace certian Java keywords and types with their equivalents in C++, as well as generate
separate header and implementation files for you (header files are so 1980's). 

Disclaimer: *This is not Skynet*. It will definitely NOT generate code that compiles, except in the
most basic case. It just does the boring work for you like typing everything twice, etc. Then you
can get on with the fun stuff like dereferencing pointers, memory management, and all that you know
and love about C.

Written by Tyler Freeman
http://odbol.com
This software is in the public domain. Do what you want with it!
"""

import sys
import re


if len(sys.argv) < 2:
	raise "Missing filename. \r\n" + instructions

fileName = sys.argv[1]

print "Processing " + fileName
f = open(fileName, 'r')
#fileContents = f.readlines()
#first massage some stylistic concerns: mainly merge block parens "{" to the same line as the function
blockFixer = re.compile(r"\)\s*$\s*{", re.MULTILINE)
fileContents = blockFixer.sub(") {\n", f.read()).splitlines(True)
f.close()

newFileName = fileName.replace(".java", ".cpp")
newFile = open(newFileName, 'w')

newHFileName = fileName.replace(".java", ".h")
newHFile = open(newHFileName, 'w')

classIdent = re.compile(r"(.*)class (\w+) (.*){", re.IGNORECASE)
funcIdent = re.compile(r"(.*)\s+(\w+)\((.*)\)\s?{", re.IGNORECASE)
fieldIdent = re.compile(r"([^=]*)\s+(\w+)\s*(=.+)?\s*;", re.IGNORECASE)

i = 0
functionStack = 0
curFunctionName = ""
className = ""
skipNextLine = 0
isAdding = False

newFile.write("#include \"" + newHFileName + "\"\n")

newHFileDef = newHFileName.replace(".", "_")
newHFile.write("#ifndef " + newHFileDef + "\n")
newHFile.write("#define " + newHFileDef + "\n")

isInFunction = False
for line in fileContents:
	i += 1
	#print "%s: %s" % (i, line)
	
	line = line.replace("String", "string").replace("final", "const").replace("@", "//@").replace("boolean", "bool").replace("this.", "this->")
	
	if className == "":
		matches = classIdent.search(line)
		if matches:
			print "found class: %s" % line
			curClassPre = matches.group(1)
			className = matches.group(2)
			curClassPost = matches.group(3)
			
			curClassPost = curClassPost.replace("extends", ":").replace("implments", ":")
			
			newHFile.write(curClassPre + " " + className + " " + curClassPost + "{\n")
			continue
	
	#only fix abstract functions, not classes
	line = line.replace("abstract", "virtual")
	
	if not isInFunction:
		matches = funcIdent.search(line)
		if matches:
			print "found function: %s" % line
			curFunctionPre = matches.group(1)
			curFunctionName = matches.group(2)
			curFunctionParams = matches.group(3)
			functionStack += 1
			
			isInFunction = True
			blockStack = 0
			
			newHFile.write(curFunctionPre + " " + curFunctionName + "(" + curFunctionParams + ");\n")
			newFile.write(curFunctionPre + " " + className + "::" + curFunctionName + "(" + curFunctionParams + ") {\n")
		else: #outside of function, must be field def.
			newHFile.write(line)

			matches = fieldIdent.search(line)
			if matches:
				print "found field: %s" % line
				curFunctionPre = matches.group(1)
				curFunctionName = matches.group(2)
				curFunctionParams = matches.group(3)
				#print "field: %s | %s | %s" % (curFunctionPre, curFunctionName, curFunctionParams)
				if curFunctionParams == None:
					curFunctionParams = ""
				else:
					curFunctionParams = " " + curFunctionParams
				
				newFile.write(curFunctionPre + " " + className + "::" + curFunctionName + curFunctionParams + ";\n")
			else: #must be a comment or something weird
				if line.strip() != "}": #don't write end of class block
					newFile.write(line)
	else:
		if line.find("{") >= 0:
			blockStack += 1
		
		if line.find("}") >= 0:	
			if blockStack == 0: #done with function
				isInFunction = False
			else:
				blockStack -= 1
				
		newFile.write(line)

newHFile.write("#endif\n")		

newFile.close()
newHFile.close()
print "Done processing " + fileName