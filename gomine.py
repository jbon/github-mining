#############################################################################################
# SCRIPT INFORMATION
#############################################################################################
"""
LICENSE INFORMATION:
---------------------
goMine.py
extract commit data from a list of repositories and saves them in two JSON files
- a json file containig the reference of all branches of all forks of the repository
- a json file containing the references of all commits of the repository
Authors: Kerstin Carola Schmidt, Jérémy Bonvoisin, Jonas Massmann
Homepage: http://opensourcedesign.cc
License: GPL v.3

PREREQUISITES: 
--------------
- a file named ".token" and including a GitHub OAUTH Access Token
- a CSV file containing a list of repositories formated as follows
  . line separator: CR
  . column separator: ;
  . no heading
  . cell content: 
      . first cell of each row : project name
      . other cells: repository references <UserName>/<RepositoryName>
- internet connection

ARGUMENTS:
----------
see help() function

To-do-list:
- check whether the repository is a fork and trow an exception if yes
"""
#############################################################################################
# HEADER
#############################################################################################

# import standard python libraries
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
# own libraries
from timeStop import timeStop
from time import sleep

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


###################################################################################################################
# FUNCTION pause
###################################################################################################################

def pause(xRateLimit, xReset):
    if xRateLimit < 10:
        secondsToWait = int((datetime.datetime.fromtimestamp(xReset)-datetime.datetime.now()).total_seconds())
        logger.info("Rate limit of allowed requests on GitHub nearly reached. Next allowance reset " + str(datetime.datetime.fromtimestamp(xReset).strftime('%Y-%m-%d %H:%M:%S')) + " "+ str(secondsToWait) + " seconds to be waited")
        #go in sleep
        for i in range(secondsToWait+1,0,-1):
            sleep(1)
            sys.stdout.write(str(i))
            k = ''.join(len(str(i))*["\b"]) 
            sys.stdout.write(k)
            sys.stdout.flush()
        logger.debug("continue process")
    
    
###################################################################################################################
# FUNCTION req
###################################################################################################################
# function for more functional github request -> Github API only returns 30 items for a normal request.
# it can be maximized to 100 -> if it's more than 100 items the next page has to be loaded and a second
# request is needed

def req(url, author):
    data_set = []
    status_codes = []
    
    response = requests.get(url, auth=(author[0],author[1]))
    logger.debug("request URL: " + url)
    logger.debug("response header: " + str(response.headers))
    #save status code
    status_codes.append(response.status_code)
    raw = response.json()
    
    #get remaining allowed requests
    try:
        pause(int(response.headers['X-RateLimit-Remaining']), int(response.headers['X-RateLimit-Reset']))
    except Exception as e: 
        print ("error at line 110")
        logger.error("Error occured: " + str(e))
        logger.error("request URL: " + url)
        logger.error("response header: " + str(response.headers))
        raise Exception('blah!')
    for line in raw:
        data_set.append(line)
        
    if len(data_set) != 0 and 'next' in response.links:
            
        while response.links['next']['url'] != response.links['last']['url']:  
            response = requests.get(response.links['next']['url'], auth=(author[0],author[1]))
            logger.debug("request URL: " + url)
            logger.debug("response header: " + str(response.headers))
            status_codes.append(response.status_code)
            raw = response.json()  
            
            #get remaining allowed requests
            try:
                pause(int(response.headers['X-RateLimit-Remaining']), int(response.headers['X-RateLimit-Reset']))
            except Exception as e: 
                print ("error at line 131")
                logger.error("Error occured: " + str(e))
                logger.error("request URL: " + url)
                logger.error("response header: " + str(response.headers))
                raise Exception('blah!')
            for line in raw:
                data_set.append(line) 
            
            """
            r = requests.get(r.links['next']['url'], auth=(author[0],author[1]))
            status_codes.append(r.status_code)
            raw = r.json()
        
        
            get remaining allowed requests
            try:
                pause(int(r.headers['X-RateLimit-Remaining']), int(r.headers['X-RateLimit-Reset']))
            except Exception as e: 
                print ("Error occured: " + str(e))
                print ("response header: " + r.headers)
                sys.exit(2)
                for line in raw: 
                    data_set.append(line)
            """
    return data_set, status_codes
    
###################################################################################################################
# FUNCTION get_all_branches
###################################################################################################################
# Returns all branches of all forks of a repository in json format as delivered by GitHub
def get_all_branches(owner, repo, logins):
    
    requestUrl = "https://api.github.com/repos/{}/{}/branches?per_page=100".format(owner,repo)
    response = requests.get(requestUrl,auth=(logins[0],logins[1]))
    logger.debug("request URL: " + requestUrl)
    logger.debug("response header: " + str(response.headers))

    #get remaining allowed requests
    try:
        pause(int(response.headers['X-RateLimit-Remaining']), int(response.headers['X-RateLimit-Reset']))
    except Exception as e: 
        print ("error at line 171")
        logger.error("Error occured: " + str(e))
        logger.error("request URL: " + requestUrl)
        logger.error("response header: " + str(response.headers))
        raise Exception('blah!')
    
    # if we get a 404, there is no point of going further. raise warning and exit
    if response.status_code == 404:
        logger.error("API request for repository "+owner+"/"+repo+" raised a 404 error")
        return []

    # if the response is not a 404, then we can go on and decode branches and forks
    branches = json.loads(response.text)
    
    if len(branches) == 100:
        logger.error("More than 100 branches -> second page needs to be loaded -> change of algorithm neccessary")

    forks, status_codes = req("https://api.github.com/repos/{}/{}/forks?per_page=100".format(owner,repo),
                logins)
    
    # if we get a 404, there is no point of going further. raise warning and exit
    if 404 in status_codes:
        logger.error("API request for repository "+owner+"/"+repo+" raised a 404 error")
        return []
    
    # parse all forks of the current repo
    for fork in forks:
        logger.info("    . in " + fork['owner']['login'] + "'s fork")
        branchesToAdd =    get_all_branches(fork['owner']['login'],fork['name'], logins)
        for itema in branchesToAdd:
            duplicate = False
            for itemb in branches:
                if itema['commit']['sha']==itemb['commit']['sha']:
                    duplicate = True
                    break
            if not duplicate:
                branches.append(itema)

    return branches  

###################################################################################################################
# FUNCTION get_predecessors
###################################################################################################################
# Returns the list of all predecessors of a given commit in the Json format provided by GitHub

def get_predecessors(commitUrl, logins):
    
    response = requests.get(commitUrl,auth=(logins[0],logins[1]))
    logger.debug("request URL: " + commitUrl)
    logger.debug("response header: " + str(response.headers))
    try:
        if len(response.json()['files']) == 0:
            logger.error('filechanges could not be downloaded for CommitUrl (stats are zero): '+ commitUrl)
    except KeyError as err: #err never used??
        logger.error('filechanges could not be downloaded for CommitUrl (stats are not available): '+ commitUrl)
    commitData = [json.loads(response.text)]
    
    #get remaining allowed requests
    try: 
        pause(int(response.headers['X-RateLimit-Remaining']), int(response.headers['X-RateLimit-Reset']))
    except Exception as e: 
        print ("error at line 232")
        logger.error("Error occured: " + str(e))
        logger.error("request URL: " + commitUrl)
        logger.error("response header: " + str(response.headers))
        raise Exception('blah!')
    try:
        sha = commitData[0]['sha']
    except Exception as e:
        print ("error at line 238")
        logger.error(commitData)
        logger.error(e)
        raise Exception('blah!')
        
    knownCommits.append(sha)
    logger.info("     - "+sha)

    # Gets the list of predecessors
    for predecessor in commitData[0]['parents']:
        if not predecessor['sha'] in knownCommits:
            commitsToAdd = get_predecessors(predecessor['url'], logins)
            knownCommits.append(predecessor['sha'])
            for commit in commitsToAdd:
                commitData.append(commit)
    
    return commitData

#############################################################################################
# INITIALISATION
#############################################################################################

# get command line arguments
try:
    options, remainder = getopt.getopt(sys.argv[1:], 'u:i:o:rdh', ['user=','input=', 'output=','rewrite','debug','help'])
except getopt.GetoptError as err:
    print(str(err))
    sys.exit(2)

# initialise the parameters to be found in the arguments
username = ''
CSVFileReference = ''
outputDir = ''
rewriteMode = False
loggerMode = logging.INFO

for option, argument in options:
    if option in ('-u','--user'):
        username = argument
    if option in ('-i','--input'):
        CSVFileReference = argument
    if option in ('-o','--output'):
        outputDir = argument
    if option in ('-r','--rewrite'):
        rewriteMode = True
    if option in ('-h','--help'):
        help()
    if option in ('-d','--debug'):
        loggerMode = logging.DEBUG

# check whether all required parameters have been given as arguments and if not throw exception and abort
if username == '':
    print ("Argument required: GitHub username. Type '-u <username>' in the command line")
    sys.exit(2)
if CSVFileReference == '':
    print ("Argument required: input CSV file. Type '-i <filepath>' in the command line")
    sys.exit(2)
if outputDir == '':
    print ("Argument required: output directory. Type '-o <directory path>' in the command line")
    sys.exit(2)
    
# initialise variables
try:
    auth = [username, open('.token','r').read()]
except FileNotFoundError as err: #err never used?
    print ("Can't start the extraction process. Token file missing. See documentation")
    exit(2) 
if not os.path.exists(outputDir):
    os.makedirs(outputDir)
t = timeStop()
knownCommits = []
    
# initialise logger
logger = logging.getLogger("mylogger")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler(os.path.join(outputDir, '_gomine'+datetime.datetime.now().strftime('_%y.%m.%d_%H.%M.%S')+'.log'), 'a', 1000000, 1)
file_handler.setLevel(loggerMode)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(loggerMode)
logger.addHandler(stream_handler)

#############################################################################################
# BODY
#############################################################################################

logger.info("opening CSV file: "+CSVFileReference)
if rewriteMode:
    logger.info("starting extraction in rewrite mode")
else:
    logger.info("starting extraction in append mode")

# parse the input file line per line and launch repo mining for each line
with open(CSVFileReference, newline='') as csvInput:
    CSVReader = csv.reader(csvInput, delimiter=';')
    for row in CSVReader:
        projectCommits = []
        projectName = row[0]
        for cell in row[1:]:
            repoRefs = cell.split('/')
            if len(repoRefs) == 2:
                repoOwner = repoRefs[0]
                repoName = repoRefs[1]
                logger.info("start extraction repo "+repoOwner+"/"+repoName)
                branchFileName = os.path.join(outputDir,projectName+"-"+repoOwner+"-"+repoName+".branches.json")
                commitFileName = os.path.join(outputDir,projectName+"-"+repoOwner+"-"+repoName+".commits.json")

                if not rewriteMode and os.path.exists(branchFileName):
                    # load branches from json file
                    logger.warning(branchFileName + " already exists. Branches references are loaded from this file. Please be aware this data may be outdated.")
                    try:
                        with open(branchFileName) as json_file:
                            branches = json.load(json_file)
                    except json.decoder.JSONDecodeError as err:
                        logger.error("unable to decode json file '" + branchFileName + "'. Error returned: " + str(err))
                else:
                    # load branches from GitHub API
                    logger.info(" - looking for branches")
                    branches = get_all_branches(repoOwner, repoName, auth)
                    with open(branchFileName, 'w') as json_file:
                        json.dump(branches, json_file)
                    logger.info("\t"+str(len(branches))+ " branches found")

                if not rewriteMode and os.path.exists(commitFileName):
                    # load commits from json file
                    logger.warning(commitFileName + " already exists. Commits references are loaded from this file. Please be aware this data may be outdated.")
                    try:
                        with open(commitFileName) as json_file:
                            commits = json.load(json_file)
                    except json.decoder.JSONDecodeError as err:
                        logger.error("unable to decode json file '" + commitFileName + "'. Error returned: " + str(err))
                else:
                    # load commits from GitHub API
                    logger.info(" - parsing branches for commits")
                    commits = []
                    for branch in branches:
                        logger.info("    . " + branch['name'])
                        if not branch['commit']['sha'] in knownCommits:
                            commitsToAdd = get_predecessors(branch['commit']['url'], auth)
                            for commit in commitsToAdd:
                                commits.append(commit)
                    logger.info("\t"+str(len(commits))+ " commits extracted")
                    """
                    verify the extraction of commits has been correctly done
                    for some reason i don't know, sometimes the extraction stops unexpectedly
                    in these cases, there is one commit whose parent is not in the commit list
                    """
                    commitShaList = []
                    for commit in commits:
                        commitShaList.append(commit['sha'])
                    for commit in commits:
                        for parent in commit['parents']:
                            if not parent['sha'] in commitShaList:
                                logger.error("commit '"+ parent['sha'] +"' is given as parent of '"+ commit['sha'] +"' but is not in the list of extracted commits of repository '"+ repoOwner+"/"+repoName +"'")

                    # write the commit json file
                    with open(commitFileName, 'w') as json_file:
                        json.dump(commits, json_file)
                    
                for commit in commits:
                    projectCommits.append(commit)
                logger.info("\t"+t.stop())
            else :
                logger.error("wrong cell format, should be 'username' '/' 'repository' - line ignored: '"+ str(cell) +"'")
        
        # write the aggregated commit file containing all commits of all repositories related to one project
        aggregatedCommitFileName = os.path.join(outputDir,projectName+".aggregated.commits.json")
        if rewriteMode or not os.path.exists(aggregatedCommitFileName):
            with open(aggregatedCommitFileName, 'w') as json_file:
                json.dump(projectCommits, json_file)
            logger.info("created aggregated commit file "+ aggregatedCommitFileName)
