#############################################################################################
# SCRIPT INFORMATION
#############################################################################################

# LICENSE INFORMATION:
#---------------------
# goMine.py
# extract commit data from a list of repositories and saves them in JSON files
# Authors: Jérémy Bonvoisin, Kerstin Carola Schmidt, Jonas Massmann
# Homepage: http://opensourcedesign.cc
# License: GPL v.3

# PREREQUISITES: 
#---------------
# - a file named ".token" and including a GitHub OAUTH Access Token
# - a CSV file containing a list of repositories formated as follows
#   . line separator: CR
#   . column separator: ;
#   . no heading
#   . cell content: 
#       . first cell of each row : project name
#       . other cells: references of repositories affiliated to this project <UserName>/<RepositoryName>

# ARGUMENTS:
# ----------
# see help() function

#############################################################################################
# HEADER
#############################################################################################

# standard python libraries
import csv
import sys
import os
import pdb
import logging
import json
import requests
import datetime
import getopt
from logging.handlers import RotatingFileHandler
from datetime import date
from time import sleep

# own libraries
from timeStop import timeStop
from GitHubAPIUtils import getAllForks, getAllBranches, prettyPrint, checkRateLimit, getCommitDetails

#############################################################################################
# FUNCTION help
#############################################################################################

def help():
    print('Required Arguments:')
    print('-u     --user     <username> GitHub user name')
    print('-i     --input    <path>     input CSV file')
    print('-o     --output   <path>     path of the directory where the JSON files should be stored')
    print('Optional Arguments:')
    print('-r     --rewrite             rewrite mode (rewrites already extracted GraphML files)')
    print('-d     --debug               debug mode (generates more traces)')
    print('-h     --help                calls help function')
    exit()
    
#############################################################################################
# INITIALISATION
#############################################################################################

# get command line arguments
try:
    options, remainder = getopt.getopt(sys.argv[1:], 'i:o:rdh', ['input=', 'output=','rewrite','debug','help'])
except getopt.GetoptError as err:
    print(str(err))
    sys.exit(2)

# initialise the parameters to be found in the arguments
inputCSVFileReference = ''
outputDir = ''
rewriteMode = False
loggerMode = logging.INFO

for option, argument in options:
    if option in ('-i','--input'):
        inputCSVFileReference = argument
    if option in ('-o','--output'):
        outputDir = argument
    if option in ('-r','--rewrite'):
        rewriteMode = True
    if option in ('-h','--help'):
        help()
    if option in ('-d','--debug'):
        loggerMode = logging.DEBUG

# check whether all required parameters have been given as arguments and if not throw exception and abort
if inputCSVFileReference == '':
    print ("Argument required: input CSV file. Type '-i <filepath>' in the command line")
    sys.exit(2)
if outputDir == '':
    print ("Argument required: output directory. Type '-o <directory path>' in the command line")
    sys.exit(2)
    
# initialise variables
try:
    auth = open('.token','r').read()
except FileNotFoundError as err:
    print ("Can't start the extraction process. Token file missing. See documentation")
    exit(2) 
if not os.path.exists(outputDir):
    os.makedirs(outputDir)
  
# initialise logger
logger = logging.getLogger("mylogger")
logger.setLevel(loggerMode)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler(os.path.join(outputDir, '_gomine'+datetime.datetime.now().strftime('_%y.%m.%d_%H.%M.%S')+'.log'), 'a', 1000000, 1)
file_handler.setLevel(loggerMode)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(loggerMode)
logger.addHandler(stream_handler)
t = timeStop()

#############################################################################################
# BODY
#############################################################################################

logger.info("opening CSV file: "+inputCSVFileReference)
if rewriteMode:
    logger.info("starting extraction in rewrite mode")
else:
    logger.info("starting extraction in append mode")

# parse the input file line per line and launch repo mining for each line
with open(inputCSVFileReference, newline='') as csvInput:
    CSVReader = csv.reader(csvInput, delimiter=';')
    for row in CSVReader:
        projectName = row[0]
        outputFileName = os.path.join(outputDir,projectName+".json")
        if not rewriteMode and os.path.exists(outputFileName):
            # load branches from json file
            logger.warning(outputFileName + " already exists. Branches references are loaded from this file. Please be aware this data may be outdated.")
        else:
            jsonOutput = []
            for cell in row[1:]:
                repoRefs = cell.split('/')
                if len(repoRefs) == 2:
                    repoOwner = repoRefs[0]
                    repoName = repoRefs[1]
                    logger.info("start extraction repo "+repoOwner+"/"+repoName)

                    # get all forks
                    forks = getAllForks(repoOwner, repoName, auth)
                    logger.info(("\t"+str(len(forks))+ " forks found"))

                    # get all branches from the repository and its forks
                    branches = getAllBranches(repoOwner, repoName, auth)
                    for fork in forks:
                        forkBranches = getAllBranches(fork["node"]["owner"]["login"], repoName, auth)
                        if forkBranches==[]:
                            logger.error("\tAPI request for repository "+fork["node"]["owner"]["login"]+"/"+repoName+" raised a 404 error")
                        branches += forkBranches
                    logger.info("\t"+str(len(branches))+ " branches found")

                    # create a non redundant list of commits
                    knownCommitReferences = []
                    for branch in branches:
                        for commit in branch["node"]["target"]["history"]["edges"]:
                            if not commit["node"]["oid"] in knownCommitReferences:
                                knownCommitReferences.append(commit["node"]["oid"])
                    logger.info("\t"+str(len(knownCommitReferences))+ " unique commits found")

                    # compile all commits form all branches of the repository and all its forks
                    commits = []
                    for sha in knownCommitReferences:
                        logger.info("\t\textracting commit info "+sha)
                        commitDetails = getCommitDetails(repoOwner, repoName, sha, auth)
                        commits.append(commitDetails)
                    logger.info("\t"+str(len(commits))+ " commits infos extracted")

                    rateLimit = checkRateLimit(auth)
                    logger.info("\tremaining ratelimit: " + str(rateLimit["remaining"]))
                    logger.info("\t"+t.stop())
                    
                    if rateLimit["remaining"] < 10:
                        secondsToWait = int((datetime.datetime.fromtimestamp(xReset)-datetime.datetime.now()).total_seconds())
                        logger.info("Rate limit of allowed requests on GitHub nearly reached. Next allowance reset " + str(datetime.datetime.fromtimestamp(rateLimit["reset"]).strftime('%Y-%m-%d %H:%M:%S')) + " "+ str(secondsToWait) + " seconds to be waited")
                        t.pause(secondsToWait)
                    
                    jsonOutput.append({"repo": {"name": repoName, "owner": repoOwner, "forks": forks, "branches": branches}})
                    
                else :
                    logger.error("wrong cell format, should be 'username' '/' 'repository' - line ignored: '"+ str(cell) +"'")
            
            # write the json file corresponding to the current project
            with open(outputFileName, 'w') as json_file:
                json.dump(commits, json_file)
            logger.info("json output file created")

