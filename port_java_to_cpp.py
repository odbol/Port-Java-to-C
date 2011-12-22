#!/bin/python
instructions = """
This script takes an Java file and auto-ports it to C++. Well, the obvious boring stuff anyway:
It will replace certian Java keywords and types with their equivalents in C++, as well as generate
separate header and implementation files for you (header files are so 1980's). 

To use:

python port_java_to_cpp.py YourJavaFile.java

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


def removePPP(s):
	return s.replace("public: ", "").replace("private: ", "").replace("protected: ", "")

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

newHFile.write("#include <string>\n") #when do you not use this, really?
newHFile.write("using namespace std;\n")

isInFunction = False
for line in fileContents:
	i += 1
	#print "%s: %s" % (i, line)
	
	line = line.replace("String", "string").replace("final", "const").replace("@", "//@").replace("boolean", "bool").replace("this.", "this->")
	line = line.replace("public ", "public: ").replace("private ", "private: ").replace("protected ", "protected: ")
	line = line.replace("package", "//package").replace("import", "//import")
	
	if className == "":
		matches = classIdent.search(line)
		if matches:
			print "found class: %s" % line
			curClassPre = matches.group(1)
			className = matches.group(2)
			curClassPost = matches.group(3)
			
			curClassPost = curClassPost.replace("extends", ":").replace("implements", ":")
			
			newHFile.write("class " + removePPP(curClassPre) + className + " " + curClassPost + "{\n")
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
			newFile.write(removePPP(curFunctionPre) + " " + className + "::" + curFunctionName + "(" + curFunctionParams + ") {\n")
		else: #outside of function, must be field def.
			if line.strip() == "}": #write end of class block
				newHFile.write("};\n")
			else:
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
				
				newFile.write(removePPP(curFunctionPre) + " " + className + "::" + curFunctionName + curFunctionParams + ";\n")
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