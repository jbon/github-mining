#############################################################################################
# SCRIPT INFORMATION
#############################################################################################

"""
TOBE UPDATED
# LICENSE INFORMATION:
#---------------------

# PREREQUISITES: 
#---------------

# ARGUMENTS:
# ----------

"""

#############################################################################################
# HEADER
#############################################################################################

# standard python libraries
import os
import pdb #Imported but unused? should we remove this?
import json
import math
import random
import hashlib
from getopt import getopt, GetoptError
import networkx as nx
import numpy as np
from collections import Counter
from sys import stdout, exit, argv
from datetime import datetime, date #Imported but unused? should we remove this?

#############################################################################################
# FUNCTION help
#############################################################################################

def help():
    print('Required Arguments:')
    print('-i     --input     <path>    path of an input JSON or directory where JSON files are stored')
    print('-o     --output     <path>   path of an input JSON or directory where JSON files are stored')
    print('Optional Arguments:')
    print('-r     --rewrite             rewrite mode (rewrites already created graphs)')
    print('-h     --help                calls help function')
    exit()
    
###################################################################################################################
# FUNCTION exportCommitGraph
###################################################################################################################

def exportCommitGraph(commits):

    G = nx.DiGraph()
    stats = {"commits" : 0, "noAuthor" : 0, "noCommitter" : 0, "noFiles": 0, "empty": 0}
    
    for commit in commits:
        
        stats["commits"] += 1
        if 'sha' in commit.keys():

            sha = commit['sha']
 
            G.add_node(
                sha,
                sha = commit['sha'],
                shortSha = commit['sha'][:7],
                authorEmail = commit['commit']['author']['email'],
                authorName = commit['commit']['author']['name'],
                authoredDate = commit['commit']['author']['date'],
                committerEmail = commit['commit']['committer']['email'],
                committerName = commit['commit']['committer']['name'],
                committedDate = commit['commit']['committer']['date'],
                message = commit['commit']['message'],
                url = commit['url']
            )
            
            try:
                G.nodes[sha]['committerLogin'] = commit['committer']['login']
            except TypeError as err:
                #print("commit " + sha + " has no attribute 'committer'.")
                stats["noCommitter"] += 1
     
            try:
                G.nodes[sha]['authorLogin'] = commit['author']['login']
            except TypeError as err:
                #print("commit " + sha + " has no attribute 'author'.")
                stats["noAuthor"] += 1
     
            try:
                G.nodes[sha]['affectedFiles'] = len(commit['files'])
            except KeyError as err:
                #print("commit " + sha + " has no attribute 'files'.")
                stats["noFiles"] += 1

        else :
            #print("invalid commit format: " + str(commit))
            stats["empty"] += 1
            
  
    for commit in commits:
        try:
            for parent in commit['parents']:
                G.add_edge(parent['sha'], commit['sha'])
        except Exception as err:
            pass

    return G, stats


###################################################################################################################
# BODY
###################################################################################################################

# get command line arguments
try:
    options, remainder = getopt(argv[1:], 'i:o:rh', ['input=', 'output=','rewrite', 'help'])
except GetoptError as err:
    print(str(err))
    exit(2)
    
# initialise the parameters to be found in the arguments
inputPath = ''
outputPath = ''
rewrite = False

# search the parameters in the arguments given to the script
for option, argument in options:
    if option in ('-i','--input'):
        inputArg = argument
    elif option in ('-o','--output'):
        outputArg = os.path.relpath(argument)
    elif option in ("-r", "--rewrite"):
        rewrite = True
    elif option in ("-h", "--help"):
        help()
       
# check whether all required parameters have been given as arguments and if not throw exception and abort
if inputArg == '':
    print("Argument required: input file or directory. Type '-i <path>' in the command line")
    exit(2)
if outputArg == '':
    print("Argument required: output file or directory. Type '-o <path>' in the command line")
    exit(2)
    
# execute options chosen by the user
if rewrite:
    print ("*executing the script in rewrite mode*")
    
if os.path.isfile(inputArg):
    if inputArg.endswith('.json'):
        inputDir, inputFileName = os.path.split(inputArg)
        filesToProcess = [inputFileName]
    else:
        print("Wrong extension of the input file '" + inputArg + "'. Should be '.json'")
elif os.path.isdir(inputArg):
    # list all existing files in the input directory ending with ".json"
    inputDir = inputArg
    print("search for files ending with '.json' in " + inputDir )
    filesToProcess = [f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, f)) and f.endswith('.json')]
    numberOfFilesFound = len(filesToProcess)
    if numberOfFilesFound == 0 :
        print("no file ending with '.json' found in " + inputDir )
        exit(2)
    else:
        print (str(numberOfFilesFound) + " files found")

# check whether the output folder exist and create it if not
if not os.path.exists(outputArg):
    os.makedirs(outputArg)
  
stats = {"commits" : 0, "noAuthor" : 0, "noCommitter" : 0, "noFiles": 0, "empty": 0}  
#build graphs for all variations for all JSON files
for fileToProcess in filesToProcess:

    fileNameRoot = os.path.splitext(fileToProcess)[0] # to remove the extension '.json'
	
    try:
        with open(os.path.join(inputDir,fileToProcess)) as json_file:
            commits = json.load(json_file)
    except json.decoder.JSONDecodeError as err:
        print("error while decoding json from file '" + fileToProcess + "'. Error returned: " + str(err))
    
    outputGraphFileName = os.path.join(outputArg, fileNameRoot+".graphml")
    if rewrite or not os.path.exists(outputGraphFileName):
        commitGraph, localStats = exportCommitGraph(commits)
        print("Commit graph created for "+fileNameRoot)
        print("\t with "+str(localStats))
        stats["commits"] += localStats["commits"]
        stats["noAuthor"] += localStats["noAuthor"]
        stats["noCommitter"] += localStats["noCommitter"]
        stats["noFiles"] += localStats["noFiles"]
        stats["empty"] += localStats["empty"]
        nx.write_graphml(commitGraph, outputGraphFileName)                
    
print("graphs created with "+str(stats))