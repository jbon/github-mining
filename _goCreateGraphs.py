#############################################################################################
# SCRIPT INFORMATION
#############################################################################################

# LICENSE INFORMATION:
# ---------------------
# goCreateGraphs.py 
# Authors: Jérémy Bonvoisin, Jonas Massmann, Rafaella Antoniou.
# Homepage: http://opensourcedesign.cc
# License: GPL v.3

# PREREQUISITES:
# ---------------
# - a directory with json files containing the description of commits as given by the github API.
#   Files names are formatted as follows <projectname>.json
#
# ARGUMENTS:
# ----------
# see help() function

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
    print('-i     --input     <path>    path of the directory where the JSON files are stored')
    print('-o     --output     <path>   path of the directory where the GraphML files should be stored')
    print('Optional Arguments:')
    print('-r     --rewrite             rewrite mode (rewrites already extracted GraphML files)')
    print('-h     --help                calls help function')
    exit()
    
###################################################################################################################
# FUNCTION exportCommitGraph
###################################################################################################################

def exportCommitGraph(commits):

    # dict for all possible git names
    committer = {'author_name':[], #What do the empty square brackets mean here?
                'author_email': [],
                'author_login': [],
                'committer_name': [],
                'committer_email': [],
                'committer_login': [],
                'color':[]
                }

    G = nx.DiGraph()
    
    for commit in commits:

        # init name for all commits
        author_name = commit['commit']['author']['name'] #Does this mean that in this case commit is the author name?
       
        # check if init name appeared in one of the name forms already
        # if not, create new dict entry with all name forms and define new color
        # TODO write shorter
        if author_name not in [x for v in committer.values() for x in v] and commit['commit']['committer']['email'] not in [x for v in committer.values() for x in v] and committer['author_login'] not in [x for v in committer.values() for x in v] and committer['committer_name'] not in [x for v in committer.values() for x in v] and committer['committer_login'] not in [x for v in committer.values() for x in v] and committer['committer_email'] not in [x for v in committer.values() for x in v]:
            committer['author_name'].append(commit['commit']['author']['name'])
            committer['author_email'].append(commit['commit']['author']['email'])
            try:
                committer['author_login'].append(commit['author']['login'])
            except:
                committer['author_login'].append('')
            committer['committer_name'].append(commit['commit']['committer']['name'])
            try:
                committer['committer_login'].append(commit['committer']['login'])
            except:
                committer['committer_login'].append('')
            committer['committer_email'].append(commit['commit']['committer']['email'])
            committer_color = getRandomColor()
            committer['color'].append(committer_color)
            
        #if name appeared already, find previeous used name and color
        else:
            for key in committer.keys():
                if author_name in committer[key]:
                    committer_color = committer['color'][committer[key].index(author_name)]
                    author_name = committer['author_name'][committer[key].index(author_name)]
                    break
                elif commit['commit']['author']['email'] in committer[key]:
                    committer_color = committer['color'][committer[key].index(commit['commit']['author']['email'])]
                    author_name = committer['author_name'][committer[key].index(commit['commit']['author']['email'])]
                    break
                elif commit['commit']['committer']['name'] in committer[key]:
                    committer_color = committer['color'][committer[key].index(commit['commit']['committer']['name'])]
                    author_name = committer['author_name'][committer[key].index(commit['commit']['committer']['name'])]
                    break
                elif commit['commit']['committer']['email'] in committer[key]:
                    committer_color = committer['color'][committer[key].index(commit['commit']['committer']['email'])]
                    author_name = committer['author_name'][committer[key].index(commit['commit']['committer']['email'])]
                    break
        if 'stats' in commit: 
            changes = str(commit['stats']['total'])
        else:
            changes = '0'
            
        G.add_node(commit['sha'],
                   sha=commit['sha'],
                   changes=changes,
                   author=author_name,
                   date=commit['commit']['committer']['date'],
                   url=commit['url'],
                   message=commit['commit']['message'],
                   color=committer_color
                   )
    
    for commit in commits:
        for parent in commit['parents']:
            G.add_edge(parent['sha'], commit['sha'], weight = random.randint(1, 200)) # weight = random.randint(1, 2000 to be replaced
    return G

###################################################################################################################
# FUNCTION exportFileGraph
###################################################################################################################

def exportFileGraph(commits, filter=[]):

    G = nx.DiGraph()
    
    nodeList = []
    errorMess = []

    # dict for all possible git names
    committer = {'author_name':[],
                'author_email': [],
                'author_login': [],
                'committer_name': [],
                'committer_email': [],
                'committer_login': [],
                'color':[]
                }

    for commit in commits:
        if 'files' in commit:
            for file in commit['files']:

                _, file_extension = os.path.splitext(file['filename'].lower())

                #TODO OTHER extensions
                if (file_extension in filter) or filter == []:
                    
                    # init name for all commits
                    author_name = commit['commit']['author']['name']
               
                    # check if init name appeared in one of the name forms already
                    # if not, create new dict entrie with all name forms and define new color
                    # TODO write shorter
                    if author_name not in [x for v in committer.values() for x in v] \
                        and commit['commit']['committer']['email'] not in [x for v in committer.values() for x in v] \
                        and committer['author_login'] not in [x for v in committer.values() for x in v] \
                        and committer['committer_name'] not in [x for v in committer.values() for x in v] \
                        and committer['committer_login'] not in [x for v in committer.values() for x in v] \
                        and committer['committer_email'] not in [x for v in committer.values() for x in v]:
                        
                        committer['author_name'].append(commit['commit']['author']['name'])
                        committer['author_email'].append(commit['commit']['author']['email'])
                        try:
                            committer['author_login'].append(commit['author']['login'])
                        except:
                            committer['author_login'].append('')
                        committer['committer_name'].append(commit['commit']['committer']['name'])
                        try:
                            committer['committer_login'].append(commit['committer']['login'])
                        except:
                            committer['committer_login'].append('')
                        committer['committer_email'].append(commit['commit']['committer']['email'])
                        committer_color = getRandomColor()
                        committer['color'].append(committer_color)
                        
                    #if name appeared already, find previeous used name and color
                    else:
                        for key in committer.keys():
                            if author_name in committer[key]:
                                committer_color = committer['color'][committer[key].index(author_name)]
                                author_name = committer['author_name'][committer[key].index(author_name)]
                                break
                            elif commit['commit']['author']['email'] in committer[key]:
                                committer_color = committer['color'][committer[key].index(commit['commit']['author']['email'])]
                                author_name = committer['author_name'][committer[key].index(commit['commit']['author']['email'])]
                                break
                            elif commit['commit']['committer']['name'] in committer[key]:
                                committer_color = committer['color'][committer[key].index(commit['commit']['committer']['name'])]
                                author_name = committer['author_name'][committer[key].index(commit['commit']['committer']['name'])]
                                break
                            elif commit['commit']['committer']['email'] in committer[key]:
                                committer_color = committer['color'][committer[key].index(commit['commit']['committer']['email'])]
                                author_name = committer['author_name'][committer[key].index(commit['commit']['committer']['email'])]
                                break
                    

                    if 'previous_filename' in file:
                        previous_filename = file['previous_filename']
                    else:
                        previous_filename = None

                    nodeList.append([file['filename'], commit['sha'], file['status'],
                                     commit['commit']['author']['date'],previous_filename])
                    
                    # Create new node for every file
                    G.add_node(nodeName(file['filename'], commit['sha']),
                               sha_commit=commit['sha'],
                               committer=author_name,
                               date=commit['commit']['committer']['date'],
                               message=commit['commit']['message'],
                               status=file['status'],
                               filename=file['filename'],
                               color=committer_color
                               )
                               
                elif not file_extension in filter and len(filter)is not 0:
                    if file_extension in omittedExtensions.keys():
                        omittedExtensions[file_extension] += 1
                    else:
                        omittedExtensions[file_extension] = 1
                        
        else:
            errorMess.append("commit " + commit['sha'] + " has no attribute 'files'. See " + commit['commit']['url'])
    
    ######## Convert list in multiple sublists
    c = Counter(elem[0] for elem in nodeList)

    sub_lists = ([[k, 4*[1], 1, 1, 1] * v for k, v in c.items()])

    for elem in sub_lists:

        counter = len(elem)
        index = 0

        for nodes in nodeList:

            if nodes[0] == elem[0]:
                elem[index + 1] = nodes[1]
                elem[index + 2] = nodes[2]
                elem[index + 3] = nodes[3]
                elem[index + 4] = nodes[4]

                # del nodeList[nodeList.index(nodes)]
                if counter - 6 < index:
                    break
                else:
                    index += 5

    ########
    
    for elem in sub_lists:

        for i in elem[3::5]:
            elem[elem.index(i)] = datetime.strptime(str(i), '%Y-%m-%dT%H:%M:%SZ')

        datelist = sorted(elem[3::5])

        for i in range(len(datelist)-1):

                older_sha = elem[elem.index(datelist[i])-2]
                newer_sha = elem[elem.index(datelist[i+1])-2]
                
                filename = elem[0]
                
                parent_node = nodeName(filename, older_sha)
                child_node = nodeName(filename, newer_sha)
                
                # TODO: check why?
                if parent_node != child_node:
                    G.add_edge(parent_node, child_node)

                ## Check if status is renamed. If true then get the previews filename and search for it in
                #  in the sublists of commits
                
                status = elem[elem.index(datelist[i])-1]
                
                if status == 'renamed':

                    for sub_elem in sub_lists:
                        filename_sublist = sub_elem[0]
                        filename_root = elem[elem.index(datelist[i])+1]
                        
                        if filename_sublist == filename_root:

                            sub_datelist = sorted(sub_elem[3::5])

                            child_node = nodeName(filename_sublist,
                                                   elem[elem.index(datelist[i])-2])
                            parent_node = nodeName(filename_root,
                                                  sub_elem[sub_elem.index(sub_datelist[len(sub_datelist)-1])-2])
                            
                            if parent_node != child_node and child_node in [k[1] for k in nodeList]:
                                    G.add_edge(parent_node, child_node)    
                
    return G, errorMess
    

###################################################################################################################
# FUNCTION exportCommitterGraph
###################################################################################################################
# Create and return a graph to display the social working together in respect of the files
# Parameter 'directed' -> True creates a directed graph, False an unidirected
# Based on Maher et al.(2010)

def exportCommitterGraph(fileGraph,selfloop=False, directed=False):
    
    # get data from fileGraph in list
    G_list = fileGraph.nodes(data=True)
    
    # get list with all authors
    authors = list(set([i[1]['committer'] for i in G_list]))
    
    filechanges = Counter(list(([i[1]['committer'] for i in G_list])))
    
    # init matrix with zeros (DIM: # authors, # authors)
    arr = np.zeros((len(authors),len(authors)))

    # get list with all edges (sha_parent, sha_child) and loop all edges
    for edge in [i for i in fileGraph.edges()]:
        
        # get author name from parent node via sha
        author_parent = [j[1]['committer'] for j in G_list][list(fileGraph.nodes()).index(edge[0])]
        # get author name from child node via sha
        author_child = [j[1]['committer'] for j in G_list][list(fileGraph.nodes()).index(edge[1])]
        
        # count +1 for existing connection between two authors
        arr[authors.index(author_parent)][authors.index(author_child)] += 1 
    
    # create directed graph
    if directed:

        # create init Graph
        G_committer = nx.DiGraph()
         
        # loop to create all nodes (1 node per author)
        for author in authors:
     
            G_committer.add_node(author,
                        author=author,
                        filechanges = filechanges[author],
                        surface = str(10*math.sqrt((np.sum(arr[authors.index(author)])))),
                        color = getRandomColor()
                        )
        
        for i, row in enumerate(arr):
            for j, column in enumerate(row):
                # connect nodes if the authors have a connection 
                # don't make a connection to the same node (can be changed)
                if not i==j and column != 0 and selfloop is False:
                    G_committer.add_edge(authors[i], authors[j], weight = (str(column)))
                elif column != 0 and selfloop is True:
                    G_committer.add_edge(authors[i], authors[j], weight = (str(column)))
    # create unidirected graph (init)
    else:
        G_committer = nx.Graph()
        
        upper_matix= np.triu(arr)
        lower_matix= np.tril(arr,-1)

        
        for i, row in enumerate(arr):
                for j, column in enumerate(row):
                    upper_matix[i,j] += lower_matix[j,i]
                    if i==j and selfloop is False:
                        upper_matix[i,j]=0
            
        # loop to create all nodes (1 node per author)
        for author in authors:
        
            G_committer.add_node(author,
                        author=author,
                        filechanges = filechanges[author],
                        surface = str(10*math.sqrt((np.sum(arr[authors.index(author)])))),
                        color = getRandomColor()
                        )

        for i, row in enumerate(upper_matix):
            for j, column in enumerate(row):
                # connect nodes if the authors have a connection 
                # don't make a connection to the same node (can be changed)
                if column != 0:
                    G_committer.add_edge(authors[i], authors[j], weight = int(column))


    # return graph
    return G_committer

###################################################################################################################
# FUNCTION getRandomColor
###################################################################################################################
# return a random color with r,g,b values

def getRandomColor():
    r = lambda: random.randint(90, 255)
    g = lambda: random.randint(90, 255)
    b = lambda: random.randint(90, 255)
    return '#%02X%02X%02X' % (r(), g(), b())
    
###################################################################################################################
# FUNCTION nodeName
###################################################################################################################
# returns a unique node name in respect of the sha and filename

def nodeName(name,sha):
    fileHash = hashlib.md5(name.encode()).hexdigest()
    nodeName = sha + "_" + fileHash
    return nodeName
    
###################################################################################################################
# BODY
###################################################################################################################

# segmentation of the file extensions in categories depending on the development activity they support 
MCAD_ext = ['.123dx', '.3dm', '.art', '.blend', '.blend1', '.crv', '.dft', '.dra', '.dwf', '.dwg', '.easm', '.epf', '.fcmacro',
    '.fcstd', '.fcstd1', '.gcode', '.iam', '.idw', '.iges', '.igs', '.ipj', '.ipn', '.ipt', '.makerbot', '.mb', '.nc', '.obj', 
    '.par', '.psm', '.scad', '.skp', '.sldasm', '.slddrw', '.sldprt', '.step', '.stl', '.stp', '.thing', '.vert', '.x_t', '.x3g']
ECAD_ext = ['.brd', '.drl', '.dsn', '.fzz', '.gbl', '.gbo', '.gbp', '.gbr', '.gbs', '.gml', '.gpi', '.gtl', '.gto', '.gtp', '.gts',
    '.kicad_mod', '.kicad_pcb', '.kicad_pcb-bak', '.pcb', '.pde', '.sch']
IMGS_ext = ['.ai', '.bmp', '.cdr', '.dxf', '.eps', '.gif', '.ico', '.jpeg', '.jpg', '.png', '.psd', '.svg', '.tiff', '.xcf', '.xmp']
DOCS_ext = ['.csv', '.docx', '.gdoc', '.htm', '.html', '.markdown', '.md', '.ods', '.odt', '.pdf', '.rtf', '.shtml',
    '.txt', '.xls', '.xlsx', '.1']
SOFT_ext = ['.bat', '.bin', '.pro', '.c', '.cc', '.cgi', '.class', '.cmp', '.cpp', '.cs', '.csproj', '.css', '.d', '.dll', '.do', '.exe',
     '.go', '.h', '.hex', '.hpp', '.inc', '.ino', '.jar', '.java', '.jnilib', '.js', '.lib', '.m', '.mk', '.o', '.pbxproj', '.php',
     '.pl', '.properties', '.py', '.pyc', '.qml', '.R', '.resources', '.resx', '.sh', '.sln', '.so', '.vb', '.xib']
DATA_ext = ['.dat', '.json', '.xml', '.ini', '.yml', '.config', '.conf', '.log', '.wav', '.err', '.settings',
     '.ipynb', '.plist', '.xlf', '.zip', '.7z']

# file extensions *probably* coming into play in hardware development
PHW_ext = MCAD_ext + ECAD_ext + IMGS_ext + DOCS_ext
# file extensions *certainly* coming into play in hardware development
CHW_ext = MCAD_ext + ECAD_ext

global omittedExtensions
omittedExtensions = {} 
   

# get command line arguments
try:
    options, remainder = getopt(argv[1:], 'i:o:rh', ['input=', 'output=','rewrite','clearscreen', 'help'])
except GetoptError as err:
    print(str(err))
    exit(2)
    
# initialise the parameters to be found in the arguments
inputDir = ''
outputDir = ''
rewrite = False
debug = False

# search the parameters in the arguments given to the script
for option, argument in options:
    if option in ('-i','--input'):
        inputDir = argument
    elif option in ('-o','--output'):
        outputDir = os.path.relpath(argument)
    elif option in ("-h", "--help"):
        help()
    elif option in ("-r", "--rewrite"):
        rewrite = True
       
# check whether all required parameters have been given as arguments and if not throw exception and abort
if inputDir == '':
    print("Argument required: input directory. Type '-i <directory path>' in the command line")
    exit(2)
if outputDir == '':
    print("Argument required: output directory. Type '-o <directory path>' in the command line")
    exit(2)
    
# execute options chosen by the user
if rewrite:
    print ("*executing the script in rewrite mode*")

# list all existing files in the input directory ending with ".commits.json"
print('search for files ending with ".json" in "' + inputDir + '"')
filesInInputDir = [f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, f)) and f.endswith('.json')]
numberOfFilesFound = len(filesInInputDir)
if numberOfFilesFound == 0 :
    print('no file ending with ".json" found in this ' + filesInInputDir + '"')
    exit(2)
else:
    print (str(numberOfFilesFound) + " files found")

# check whether the output folder exist and create it if not
if not os.path.exists(outputDir):
    os.makedirs(outputDir)
    
#build graphs for all variations for all JSON files
for JsonFile,i in zip(filesInInputDir,range(0,len(filesInInputDir))):
    fileNameRoot = os.path.splitext(os.path.splitext(os.path.splitext(JsonFile)[0])[0])[0] # to remove '.aggregated.commits.json'
    commitGraph = None
    fileGraphALL = None
    fileGraphPHW = None
    fileGraphCHW = None
    
	# processbar
    stdout.write('\r')
    stdout.write("[%-30s] %d%%" % ('=' * int(i*30/len(filesInInputDir)+1),  i*100/len(filesInInputDir)+1))
    stdout.flush()
    print(" " + fileNameRoot)
	
    # get the list of commits from the JSON file
    try:
        with open(os.path.join(inputDir,JsonFile)) as json_file:
            commits = json.load(json_file)
    except json.decoder.JSONDecodeError as err:
        print("error while decoding json from file '" + JsonFile + "'. Error returned: " + str(err))
    
    # 1 - commit graph
    graphmlFile = os.path.join(outputDir, fileNameRoot+".commits.ALL.graphml")
    if rewrite or not os.path.exists(graphmlFile):
        commitGraph = exportCommitGraph(commits)
        nx.write_graphml(commitGraph, graphmlFile)                
    
    # 2.1 - filechange graph - ALL
    graphmlFile = os.path.join(outputDir, fileNameRoot +".filechanges.ALL.graphml")
    if rewrite or not os.path.exists(graphmlFile):
        fileGraphALL, errorMess = exportFileGraph(commits)
        if debug:
            for mess in errorMess:
                print(mess)
        nx.write_graphml(fileGraphALL, graphmlFile)    
    
    
    # 2.2 - filechange graph - PHW
    graphmlFile = os.path.join(outputDir, fileNameRoot +".filechanges.PHW.graphml")
    if rewrite or not os.path.exists(graphmlFile):
        fileGraphPHW, errorMess = exportFileGraph(commits, PHW_ext)
        if debug:
            for mess in errorMess:
                print(mess)
        nx.write_graphml(fileGraphPHW, graphmlFile)                

    # 2.3 - filechange graph - CHW
    graphmlFile = os.path.join(outputDir, fileNameRoot +".filechanges.CHW.graphml")
    if rewrite or not os.path.exists(graphmlFile):
        fileGraphCHW, errorMess = exportFileGraph(commits, CHW_ext)
        if debug:
            for mess in errorMess:
                print(mess)
        nx.write_graphml(fileGraphCHW, graphmlFile)                
    
    # 3.1 - committer graph - ALL
    graphmlFile = os.path.join(outputDir, fileNameRoot +".committers.ALL.graphml")
    if rewrite or not os.path.exists(graphmlFile):
        if fileGraphALL == None:
            fileGraphALL = nx.read_graphml(os.path.join(outputDir, fileNameRoot+".filechanges.ALL.graphml"))
        nx.write_graphml(exportCommitterGraph(fileGraphALL, selfloop, mode), graphmlFile) 

    # 3.2 - committer graph - PHW
    graphmlFile = os.path.join(outputDir, fileNameRoot +".committers.PHW.graphml")
    if rewrite or not os.path.exists(graphmlFile):
        if fileGraphPHW == None:
            fileGraphPHW = nx.read_graphml(os.path.join(outputDir, fileNameRoot +".filechanges.PHW.graphml"))
        nx.write_graphml(exportCommitterGraph(fileGraphPHW,selfloop, mode), graphmlFile)                

    # 3.3 - committer graph - CHW
    graphmlFile = os.path.join(outputDir, fileNameRoot +".committers.CHW.graphml")
    if rewrite or not os.path.exists(graphmlFile):
        if fileGraphCHW == None:
            fileGraphCHW = nx.read_graphml(os.path.join(outputDir, fileNameRoot +".filechanges.CHW.graphml"))
        nx.write_graphml(exportCommitterGraph(fileGraphCHW,selfloop, mode), graphmlFile)                    