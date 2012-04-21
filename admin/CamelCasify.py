#!/usr/bin/env python

import os
import re
import subprocess
import copy
import string

rootdir = "/home/jeff/src/tomahawk-virgin/src"

counter = 0
for root, dirs, files in os.walk( rootdir ):
    for currfile in files:
        if "thirdparty" in os.path.join( root, currfile ):
            continue
        if "taghandlers" in os.path.join( root, currfile ):
            continue
        if currfile == "main.cpp" or currfile == "CMakeLists.txt" or currfile == "resources.qrc" or currfile == "gen_schema.h.sh":
            continue
        if re.match(r"^[a-z1-9_\.]+$", currfile):
            counter = counter + 1

print "There are %i files left" % counter
            
for root, dirs, files in os.walk( rootdir ):
    files.sort()
    for currfile in files:
        if "thirdparty" in os.path.join( root, currfile ):
            continue
        if "taghandlers" in os.path.join( root, currfile ):
            continue
        if currfile == "main.cpp" or currfile == "CMakeLists.txt" or currfile == "resources.qrc" or currfile == "gen_schema.h.sh":
            continue
        #if not currfile == "lineedit_p.h":
            #continue
        if re.match(r"^[a-z1-9_\.]+$", currfile):
            #it's all lower case
            os.chdir( os.path.dirname( os.path.join( root, currfile ) ) )
            print "\n\nFile is %s" % currfile
            newname = raw_input("Please input the CamelCase name to use: ")
            print "Moving to %s" % os.path.join( root, newname )
            output = subprocess.check_output( [ "git", "mv", currfile, newname ], cwd=os.getcwd() )
            print output
            currfile = string.replace( currfile, ".", "\." )
            newname = string.replace( newname, ".", "\." )
            for root2, dirs2, files2 in os.walk( rootdir ):
                for currfile2 in files2:
                    #currfile2 = string.replace( currfile2, ".", "\\." )
                    blah = False
                    try:
                        subprocess.check_call( [ "grep", currfile, os.path.join( root2, currfile2 ) ], stderr=None )
                        blah = True
                    except:
                        pass
                    if blah:
                        subprocess.check_call( [ 'sed', '-i', '-e s/\"%s\"/\"%s\"/g' % ( currfile, newname ), '-e s/<%s>/<%s>/g' % ( currfile, newname ), '-e s/>%s</>%s</g' % ( currfile, newname ), '-e s/\/%s/\/%s/g' % ( currfile, newname ), '-e s/ %s/ %s/g' % ( currfile, newname ), '-e s/ui_%s/ui_%s/g' % ( currfile, newname ), os.path.join( root2, currfile2 ) ], cwd=rootdir )
                    