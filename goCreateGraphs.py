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
import json
from getopt import getopt, GetoptError
import networkx as nx
from sys import exit, argv
import numpy

#############################################################################################
# FUNCTION
#############################################################################################

def help():
    print('Required Arguments:')
    print('-i     --input     <path>    path of a directory where JSON files are stored')
    print('-o     --output    <path>    path of a directory where graphs will be saved')
    print('-t     --type      <type>    type of graph to be created. Type can be:')
    print('                                  - "commit" for commit networks') 
    print('                                  - "committer" for coedition grahps') 
    print('Optional Arguments:')
    print('-r     --rewrite             rewrite mode (rewrites already created graphs)')
    print('-h     --help                calls help function')
    exit()
  
  
###################################################################################################################
# FUNCTION
###################################################################################################################
# Creates and returns a file co-edition graph

def getCommitterGraph(commits):
    
    committers, stats = getCommitters(commits)
    numberOfCommitters = len(committers)

    # create adjacency matrix
    adjacencyMatrix = numpy.zeros([numberOfCommitters, numberOfCommitters])
    
    
    # fill adjacency matrix
    for commit in commits:
        if "files" in commit.keys():
                for file in commit['files']:
                    if not file['status']=='added':
                        # recursively look for commit parents and check if the file has been edited
                        exitCondition = False
                        referenceCommit = commit
                        while not exitCondition:
                            if not referenceCommit['parents']: # there is no parent, we stop
                                exitCondition = True
                            else:
                                for parent in referenceCommit['parents']:
                                    referenceCommit = [ x for x in commits if x["sha"] == parent['sha']]
                                    if any(x['filename'] == file['filename'] for x in referenceCommit['files']): # is the file affected by the referenceCommit?
                                        exitCondition = True                               
                        
                                
                        
                
                
        else:
            #print("commit " + sha + " has no attribute 'files'.")
            stats["noFiles"] += 1        

    # transform the adjacency matrix in a graph
    G = nx.MultiDiGraph()

    # return graph
    return G, stats
  
###################################################################################################################
# FUNCTION
###################################################################################################################
# Creates and returns a list of people identified by login, name and email

def getCommitters(commits):

    stats = {"commits" : 0, "noAuthor" : 0, "noCommitter" : 0, "noFiles": 0, "empty": 0}

    # fetch author and committer infos from commits and put them in a list of dicts {'login':, 'name':, 'email':}
    committers = []

    stats["commits"] += 1
    for commit in commits:

        if "commit" in commit.keys():
            author = {}
            author['email'] = commit['commit']['author']['email']
            author['name'] = commit['commit']['author']['name']
            try:
                author['login'] = commit['author']['login']
            except TypeError as err:
                #print("commit " + commit['sha'] + " has no attribute 'author'.")
                author['login'] = ""
                stats["noAuthor"] += 1
            
            committer = {}
            committer['email'] = commit['commit']['committer']['email']
            committer['name'] = commit['commit']['committer']['name']
            try:
                committer['login'] = commit['committer']['login']
            except TypeError as err:
                #print("commit " + commit['sha'] + " has no attribute 'committer'.")
                committer['login'] = ""
                stats["noCommitter"] += 1

            if not committer in committers:
                committers.append(committer)
            if not author in committers:
                committers.append(author)
        else :
            #print("invalid commit format: " + str(commit))
            stats["empty"] += 1
            
    # merge similar profiles into a list of dicts {'uniqueID', 'login(s)':, 'name(s)':, 'email(s)':} 
    uniqueCommitters = []
    for committer in committers:
        toBeMerged = [x for x in committers if \
            x['login']!= "" and x['login']==committer['login'] or \
            x['name']!= "" and x['name']==committer['name'] or \
            x['name']!= "" and x['email']==committer['email'] \
        ]
        logins = list(set(map(lambda x : x['login'], toBeMerged))) # converting to a set removes the duplicates
        names = list(set(map(lambda x : x['name'], toBeMerged)))
        emails = list(set(map(lambda x : x['email'], toBeMerged)))

        uniqueCommitter = { \
            'uniqueID': len(uniqueCommitters), \
            'logins': logins, \
            'names': names, \
            'emails': emails \
        }
        
        uniqueCommitters.append(uniqueCommitter)

    return uniqueCommitters, stats
    
###################################################################################################################
# FUNCTION
###################################################################################################################

def getCommitGraph(commits):

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

GRAPH_TYPES = ["commit", "committer"]

# get command line arguments
try:
    options, remainder = getopt(argv[1:], 'i:o:t:rh', ['input=', 'output=', 'type=', 'rewrite', 'help'])
except GetoptError as err:
    print(str(err))
    exit(2)
    
# initialise the parameters to be found in the arguments
inputDir = ''
outputDir = ''
graphType = ''
rewrite = False

# search the parameters in the arguments given to the script
for option, argument in options:
    if option in ('-i','--input'):
        inputDir = argument
    elif option in ('-o','--output'):
        outputDir = os.path.relpath(argument)
    elif option in ('-t','--type'):
        graphType = os.path.relpath(argument)
    elif option in ("-r", "--rewrite"):
        rewrite = True
    elif option in ("-h", "--help"):
        help()
       
# check whether all required parameters have been given as arguments and if not throw exception and abort
if inputDir == '':
    print("Argument required: input directory. Type '-i <path>' in the command line. Type '-h' for further help.")
    exit(2)
if outputDir == '':
    print("Argument required: output directory. Type '-o <path>' in the command line. Type '-h' for further help.")
    exit(2)
if graphType == '':
    print("Argument required: type of graph to generate. Type '-t <type>' in the command line. Type '-h' for further help.")
    exit(2)
if not graphType in GRAPH_TYPES:
    print("Graph type '"+graphType+"' not recognized. Should be one of the following options: "+str(GRAPH_TYPES))
    exit(2)
    
# execute options chosen by the user
if rewrite:
    print ("executing the script in rewrite mode")
    
if os.path.exists(inputDir) and os.path.isdir(inputDir):
    # list all existing files in the input directory ending with ".json"
    print("search for files ending with '.json' in " + inputDir )
    filesToProcess = [f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, f)) and f.endswith('.json')]
    numberOfFilesFound = len(filesToProcess)
    if numberOfFilesFound == 0 :
        print("no file ending with '.json' found in " + inputDir )
        exit(2)
    else:
        print (str(numberOfFilesFound) + " files found")
else:
    print(inputDir+" either does not exist or is not a directory")
    exit(2)
    
        
# check whether the output folder exist and create it if not
if not os.path.exists(outputDir):
    os.makedirs(outputDir)
  
stats = {"commits" : 0, "noAuthor" : 0, "noCommitter" : 0, "noFiles": 0, "empty": 0}  
#build graphs for all variations for all JSON files
for fileToProcess in filesToProcess:

    fileNameRoot = os.path.splitext(fileToProcess)[0] # to remove the extension '.json'
	
    try:
        with open(os.path.join(inputDir,fileToProcess)) as json_file:
            commits = json.load(json_file)

        outputGraphFileName = os.path.join(outputDir, fileNameRoot+".graphml")
        
        if rewrite or not os.path.exists(outputGraphFileName):
            if graphType == "commit":
                graph, localStats = getCommitGraph(commits)
            if graphType == "committer":
                graph, localStats = getCommitterGraph(commits)
            
            print("Graph created for "+fileNameRoot)
            print("\t with "+str(localStats))
            stats["commits"] += localStats["commits"]
            stats["noAuthor"] += localStats["noAuthor"]
            stats["noCommitter"] += localStats["noCommitter"]
            stats["noFiles"] += localStats["noFiles"]
            stats["empty"] += localStats["empty"]
            nx.write_graphml(graph, outputGraphFileName)                
        else:
            print("Graph for "+fileNameRoot + "already exists")            
            
    except json.decoder.JSONDecodeError as err:
        print("error while decoding json from file '" + fileToProcess + "'. Error returned: " + str(err))
    
print("graphs created with "+str(stats))