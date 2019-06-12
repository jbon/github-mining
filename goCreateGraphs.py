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
    
    users = getUsers(commits)
    numberOfUsers = len(users)

    # create adjacency matrix
    adjacencyMatrix = numpy.zeros([numberOfUsers, numberOfUsers])
    
       
    # fill adjacency matrix
    for commit in commits:
        # GitHub Issue #13 Complex interaction cases in commits 
        currentCommitter = matchUser(fetchUserInfo(commit, "author"), users)
        print ("    current commit :" + commit['url'])
        if "files" in commit.keys():
                for file in commit['files']:
                    print ("        looking for interactions in file" + file["filename"])
                    if not file['status']=='added':
                        lastEdits = []
                        for parent in commit['parents']:
                            parentFullDetails = [ x for x in commits if x["sha"] == parent['sha']]
                            if len(parentFullDetails)==1:
                                lastEdits += searchLastEdit(commits, parentFullDetails[0], file["filename"])
                            else:
                                print ("error: no commit or more than one commit corresponding to sha: " + parent['sha'] + ": "+ str(parentFullDetails))
                        #print("     edits found " + str(len(lastEdits)) + " " + str([x['sha'] for x in lastEdits]))
                        # the list of returned commits should contain:
                        #     - at least one item, since you would expect that a file which is "modified" in the current commit has at least been "added" in a previous commit, if not "modified"
                        #     - max 2 different items, since a commit can have max 2 parents
                        #     - nonetheless, the list of returned items can contain duplicates, since the recursive search can find a commit following different branches    
                        lastEdits = [element for index, element in enumerate(lastEdits) if element not in lastEdits[index + 1:]] # removes the duplicates
                        #print("edits found " + str(len(lastEdits)) + " " + str([x['sha'] for x in lastEdits]))
                        if len(lastEdits)==0 or len(lastEdits)>2:
                            print ("error - returned list of commits should contain 1 or 2 items: " + str(lastEdits))
                            print ("    current commit : " + commit['url'])
                            print ("    current file :" + file["filename"])
                        for lastEdit in lastEdits:
                            lastAuthoringUser = matchUser(fetchUserInfo(lastEdit, "author"), users)
                            lastCommittingUser = matchUser(fetchUserInfo(lastEdit, "committer"), users)
                            #print(lastAuthoringUser)
                            #print (lastAuthoringUser['uniqueID'])
                            #print(lastCommittingUser)
                            #print (lastCommittingUser['uniqueID'])
                            adjacencyMatrix[lastCommittingUser['uniqueID'],currentCommitter['uniqueID']] += 1
                            if lastAuthoringUser!=lastCommittingUser:
                                adjacencyMatrix[lastAuthoringUser['uniqueID'],currentCommitter['uniqueID']] += 1

    # transform the adjacency matrix in a graph
    G = nx.DiGraph()

    # create nodes
    for i in range(0,numberOfUsers):
        user = [x for x in users if x['uniqueID']==i][0]
        G.add_node(
            i, # corresponds to uniqueID of the user
            logins = user['logins'],
            names = user['names'],
            emails = user['emails']
        )
    #print(G.nodes(data=True))

    # create nodes
    for i in range(0,numberOfUsers):
        for j in range(0,numberOfUsers):
            if adjacencyMatrix[i,j]!=0:
                G.add_edge(i, j, weight=adjacencyMatrix[i,j])
    #print(G.edges(data=True))
        
    # return graph
    return G
 
###################################################################################################################
# FUNCTION
###################################################################################################################
# Creates and returns a list of users without duplicates where users are identified by a list of possible logins, names and emails

# TODO issue #12 - check the quality of the extracted commits during extraction
# move the following to gomine.
#print("commit " + commit['sha'] + " has no attribute 'committer'.")
#print("invalid commit format: " + str(commit))
#print("commit " + commit['sha'] + " has no attribute 'author'.")
#stats = {"commits" : 0, "noAuthor" : 0, "noCommitter" : 0, "noFiles": 0, "empty": 0}

def getUsers(commits):

    # fetch author and committer infos from commits and put them in a list of dicts {'login':, 'name':, 'email':}
    users = []
    for commit in commits:
        if "commit" in commit.keys():
            author = fetchUserInfo(commit, 'author')
            committer = fetchUserInfo(commit, 'committer')
            if not committer in users:
                users.append(committer)
            if not author in users:
                users.append(author)

    print ("    " + str(len(users)) + " users found: " + str(users))
    # merge similar profiles into a list of dicts {'uniqueID':, 'login(s)':, 'name(s)':, 'email(s)':}
    uniqueUsers = []
    for user in users:
    
        # fetch users having something in common with the tested user in the list of unmerged users
        usersToBeMerged = [x for x in users if \
            user['login'] != "" and user['login'] == x['login'] or \
            user['name'] != "" and user['name'] == x['name'] or \
            user['email'] != "" and user['email'] == x['email'] \
        ]
        # fetch users having something in common with the tested user in the list of merged users
        uniqueUsersToBeMerged = [x for x in uniqueUsers if \
            user['login'] != "" and user['login'] in x['logins'] or \
            user['name'] != "" and user['name'] in x['names'] or \
            user['email'] != "" and user['email'] in x['emails'] \
        ]
        # compile all the infos of these duplicate users
        logins = list(map(lambda x : x['login'], usersToBeMerged)) + [item for sublist in list(map(lambda x : x['logins'], uniqueUsersToBeMerged)) for item in sublist]
        names = list(map(lambda x : x['name'], usersToBeMerged)) + [item for sublist in list(map(lambda x : x['names'], uniqueUsersToBeMerged)) for item in sublist]
        emails = list(map(lambda x : x['email'], usersToBeMerged)) + [item for sublist in list(map(lambda x : x['emails'], uniqueUsersToBeMerged)) for item in sublist]
                
        uniqueUser = { \
            'uniqueID': None, \
            'logins': list(set(logins)), \
            'names': list(set(names)), \
            'emails': list(set(emails)) \
        } # converting to a set removes the duplicates

        # replace the merged users in the list of unique users with merged versions of these same users
        for userToRemove in uniqueUsersToBeMerged:
            uniqueUsers.remove(userToRemove)
        uniqueUsers.append(uniqueUser)
 
    for i, uniqueUser in enumerate(uniqueUsers):
        uniqueUser['uniqueID'] = i

    print ("    " + str(len(uniqueUsers)) + " unique users identified: " + str(uniqueUsers))
 
    return uniqueUsers

###################################################################################################################
# FUNCTION
###################################################################################################################
# fetches user info from a commit and put them in a dict {'login':, 'name':, 'email':}
# all strings are lowercased
# role is either "author" or "committer"

def fetchUserInfo(commit, role):

    user = {}
    user['email'] = commit['commit'][role]['email'].lower()
    user['name'] = commit['commit'][role]['name'].lower()
    try:
        user['login'] = commit[role]['login'].lower()
    except TypeError as err:
        user['login'] = ""
    return user

###################################################################################################################
# FUNCTION
###################################################################################################################
# match a user from a list of users and returns the found user dict

def matchUser(user, userList):

    foundUser = [x for x in userList if \
        user['login'] != "" and user['login'] in x['logins'] or \
        user['name'] != "" and user['name'] in x['names'] or \
        user['email'] != "" and user['email'] in x['emails'] \
    ]
    if len(foundUser)!=1:
        raise Exception("there is either no user or more than one user that fit with the following data: "+ str(user) + " returned users " +str(foundUser))
    return foundUser[0]

###################################################################################################################
# FUNCTION
###################################################################################################################
# searches the last commit in the history of the given commit where the file has been edited
def searchLastEdit(commits, commit, fileName):

    #print (commit['url'])
    lookedForCommit = []
    fileFound = False
        
    try:
        for file in commit['files']:
            if file['filename'].split("/")[-1]==fileName.split("/")[-1]: # we only look at the filename and not the path
                fileFound = True
    except KeyError as err:
        pass   
        
    if fileFound: # is the file affected by the current commit?
        #print("found commit : " + commit['sha'])
        lookedForCommit+= [commit]

    else:
        for parent in commit['parents']:
            parentFullDetails = [ x for x in commits if x["sha"] == parent['sha']]
            if len(parentFullDetails)==1:
                lookedForCommit+= searchLastEdit(commits, parentFullDetails[0], fileName)
            else:
                print ("error: no commit or more than one commit corresponding to sha: " + parent['sha'] + ": "+ str(parentFullDetails))

    return lookedForCommit
   
###################################################################################################################
# FUNCTION
###################################################################################################################

def getCommitGraph(commits):

    G = nx.DiGraph()
    
    for commit in commits:
        
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
                pass
     
            try:
                G.nodes[sha]['authorLogin'] = commit['author']['login']
            except TypeError as err:
                pass
                
            try:
                G.nodes[sha]['affectedFiles'] = len(commit['files'])
            except KeyError as err:
                pass            
  
    for commit in commits:
        try:
            for parent in commit['parents']:
                G.add_edge(parent['sha'], commit['sha'])
        except Exception as err:
            pass

    return G


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
  
#build graphs for all variations for all JSON files
for fileToProcess in filesToProcess:

    fileNameRoot = os.path.splitext(fileToProcess)[0] # to remove the extension '.json'
	
    try:
        with open(os.path.join(inputDir,fileToProcess)) as json_file:
            commits = json.load(json_file)

        outputGraphFileName = os.path.join(outputDir, fileNameRoot+".gml")
        
        if rewrite or not os.path.exists(outputGraphFileName):
            print("Creating graph for "+fileNameRoot)
            if graphType == "commit":
                graph = getCommitGraph(commits)
            if graphType == "committer":
                graph = getCommitterGraph(commits)
            
            nx.write_gml(graph, outputGraphFileName)                
            print("    Graph created with "+str(len(graph.nodes()))+ " nodes")
        else:
            print("Graph for "+fileNameRoot + "already exists")            
            
    except json.decoder.JSONDecodeError as err:
        print("error while decoding json from file '" + fileToProcess + "'. Error returned: " + str(err))
    
print("termniated withour errors")