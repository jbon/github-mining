#############################################################################################
# SCRIPT INFORMATION
#############################################################################################

# LICENSE INFORMATION:
# ---------------------
# analysis.py 
# Authors: Jérémy Bonvoisin, Jonas Massmann
# Homepage: http://opensourcedesign.cc
# License: GPL v.3

# PREREQUISITES:
# ---------------
# - a directory with json files containing the description of commits as given by the github API.
#   Files names are formatted as follows <GitHubUser>-<GitHubRepo>.commits.json
# - non standard libraries (install with <libraryName>):
#   . NetworkX (https://networkx.github.io/documentation/stable/reference/index.html)
#
# ARGUMENTS:
# -----------
# see help() function

#############################################################################################
# HEADER
#############################################################################################

# standard python libraries
import os
import csv
from getopt import getopt, GetoptError
import matplotlib.pyplot as plt
import networkx as nx
from sys import stdout, exit, argv

#############################################################################################
# FUNCTION help
#############################################################################################

def help():
    print('Required Arguments:')
    print('-i     --input     <path>    path of the directory where the GraphML files are stored')
    print('-o     --output     <path>   path of the directory where the figures should be stored')
    print('Optional Arguments:')
    print('-w     --weights             use edge weigts for clustering coefficients')
    print('-c     --clearscreen         clear sceen before processing')
    print('-h     --help                calls help function')
    exit()    

    
#############################################################################################
# FUNCTION loadGraphMLs
#############################################################################################
def loadGraphMLs(inputDir, extension):            

    graphs = []
    GraphMLFiles = [f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, f)) and f.lower().endswith(extension)]
    numberOfGraphMLFiles = len(GraphMLFiles)
    print(str(numberOfGraphMLFiles) + ' files found ending with "' + extension + '"')
    for file,i in zip(GraphMLFiles,range(0,len(GraphMLFiles))):
        graphs.append(nx.read_graphml(os.path.join(inputDir, file)))
        # processbar
        stdout.write('\r')
        stdout.write("[%-30s] %d%%" % ('=' * int(i*30/len(GraphMLFiles)+1),  i*100/len(GraphMLFiles)+1))
        stdout.flush()
    print('\r')
    return graphs

#############################################################################################
# FUNCTION computeIndicators
#############################################################################################

def computeIndicators(committerGraphs, repoReferences, useWeights=False):
   
    projectNames = [] # to host project names
    committersNumbers = [] # to host numbers of committers 
    completenessIndex = [] # to host graph completeness values
    centralizationIndex = [] # to host the graph centrality values 
    clusteringIndex = [] # to host the graph modularity values 
    
    #########################################################################################
    ## Analyse the number of edges in respect to the number of committers ###################
    #########################################################################################
    #indicators are only available for unidirected graphs
    
    for committerGraph, file in zip(committerGraphs, repoReferences):

        # convert directed graph into unidirected graph
        if nx.is_directed(committerGraph):
            committerGraph_undirected = nx.to_undirected(committerGraph) 
            committerGraph_undirected = nx.Graph(committerGraph_undirected)
        else: 
            committerGraph_undirected = committerGraph
        
        # add project to the list and get the corresponding number of committers 
        projectNames.append(file)
        numberOfCommitters = nx.number_of_nodes(committerGraph_undirected) # number of committers in this project
        committersNumbers.append(numberOfCommitters)

        # Completeness
        # ----------
        # if there is more than one committer, we can calculate a completeness
        if numberOfCommitters > 1:
            # calculate the completeness of the graph, that is, the position in the scale between:
            #  - 0 edge (the graph is entirely disconnected)
            #  - n*(n-1), where n is the number of nodes (each node is connected with all other nodes)
            scaleMin = 0
            scaleMax = len(committerGraph_undirected)*(len(committerGraph_undirected)-1)/2
            completenessIndex.append((nx.number_of_edges(committerGraph_undirected)-scaleMin)/(scaleMax-scaleMin))
        else:
            completenessIndex.append(float('nan')) # no Completeness value can be calculated
        
        '''
        Centrality
        ----------
        after "Social Network Analysis: Methods and Applications", Stanley Wasserman, Katherine Faust
        --> Degree is the number of nodes that a focal node is connected to, 
            and measures the involvement of the node in the network
        https://books.google.de/books?id=CAm2DpIqRUIC&printsec=frontcover&redir_esc=y#v=onepage&q=Centrality&f=false
        https://cs.brynmawr.edu/Courses/cs380/spring2013/section02/slides/05_Centrality.pdf
        '''
        
        # get degree of every node
        degree = nx.degree(committerGraph_undirected)
        
        # By Freeman (1977) definition:
        if ((numberOfCommitters-1)*(numberOfCommitters-2)) is not 0 and len(degree) is not 0:
            # maximum degree
            c_star = max([x[1] for x in degree])
            av = sum([c_star-abs(c_a) for c_a in [x[1] for x in degree]])/((numberOfCommitters-1)*(numberOfCommitters-2))
            centralizationIndex.append(av)
        else:
            centralizationIndex.append(float('nan')) # no Centrality value can be calculated
            
        # Modularity / Clustering
        # ----------
        # after "Generalizations of the clustering coefficient to weighted complex networks", 
        # J. Saramäki, M. Kivelä, J.-P. Onnela, K. Kaski, and J. Kertész,
        # Physical Review E, 75 027105 (2007). 
        # http://jponnela.com/web_documents/a9.pdf
        # Corresponding Networkx function:
        # https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.cluster.clustering.html?highlight=clustering#networkx.algorithms.cluster.clustering
        
        # Note: Self loops are ignored in nx.clustering function!
        if useWeights:
            clustering_coefficients = nx.clustering(committerGraph_undirected, weight='weight')
        else:
            clustering_coefficients = nx.clustering(committerGraph_undirected)
            
        # average over all clustering_coefficients
        if len(clustering_coefficients) is not 0:
            clusteringIndex.append(
                sum(clustering_coefficients.values())/len(clustering_coefficients))
        else:
            clusteringIndex.append(float('nan')) # no Modularity value can be calculated

    return committersNumbers, completenessIndex, centralizationIndex, clusteringIndex


###################################################################################################################
# BODY
###################################################################################################################

#initialisation
#####################

# declare global variables
global inputDir, outputDir

# get command line arguments
try:
    options, remainder = getopt(argv[1:], 'i:o:chw', ['input=', 'output=','', 'clearscreen', 'help'])
except GetoptError as err:
    print(str(err))
    exit(2)
    
# initialise the parameters to be found in the arguments
inputDir = ''
outputDir = ''
clearscreen = False
useWeights = False

# search the parameters in the arguments given to the script
for option, argument in options:
    if option in ('-i','--input'):
        inputDir = argument
    elif option in ('-o','--output'):
        outputDir = os.path.relpath(argument)
    elif option in ('-c','--clearscreen'):
        clearscreen = True
    elif option in ('-w','--weights'):
        useWeights = True
        print('*use edge weights for caluclation of clustering coefficients*')
    elif option in ("-h", "--help"):
        help()
       
# check whether all required parameters have been given as arguments and if not throw exception and abort
if inputDir == '':
    print("Argument required: input directory. Type '-i <directory path>' in the command line")
    exit(2)
if outputDir == '':
    print("Argument required: output directory. Type '-o <directory path>' in the command line")
    exit(2)

# check whether the output folder exist and create it if not
if not os.path.exists(outputDir):
    os.makedirs(outputDir)
    
# execute options chosen by the user
if clearscreen:
    os.system('cls')

# define the series of files to look at and analyze
seriesNames = ['committers.all.graphml', 'committers.phw.graphml', 'committers.chw.graphml']

repoReferences = [ \
    os.path.splitext(os.path.splitext(os.path.splitext(f)[0])[0])[0] 
    for f in os.listdir(inputDir) \
    if os.path.isfile(os.path.join(inputDir, f)) and f.lower().endswith(seriesNames[0].lower())]
for serie in seriesNames:
    columnsToExport = [repoReferences]
    #load required graphs
    loadedGraph = loadGraphMLs(inputDir, serie)
    if len(loadedGraph) == len(repoReferences):
        nrCommitters, completeness, centralization_index, network_clustering = \
            computeIndicators(loadedGraph, repoReferences, useWeights)
        columnsToExport.append(nrCommitters)
        columnsToExport.append(completeness)
        columnsToExport.append(centralization_index)
        columnsToExport.append(network_clustering)
    else:
        print ("error, all file series should have the same number of elements")
        sys.exit(2)

    #transpose the list of list to save data as CSV and export as CSV file
    #####################
    CSVdata = map(list, zip(*columnsToExport))
    with open(os.path.join(outputDir, 'graphAnalysis'+serie+'.csv'),'w', newline='') as csvOutput:
            CSVWriter = csv.writer(csvOutput, delimiter=";")
            # CSVWriter.writerow(headline)
            for column in CSVdata:
                CSVWriter.writerow(column)


    ## Box PLOT number of committers ############################################################
    #############################################################################################
    # notched plot
    plt.figure(figsize=(2,7))
    bplot = plt.boxplot(nrCommitters,vert=True, patch_artist=True)

    for patch in bplot['boxes']:
        patch.set_facecolor('#b4b4b4')
    for median in bplot['medians']:
        median.set(color='k')

    ax = plt.gca()
    ax.set_ylabel('Number of committers')
    ax.get_xaxis().set_ticks([])
    ax.set_ylim([0,40])
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.savefig(os.path.join(outputDir, 'committers_per_project.'+serie+'.boxplot.svg'), bbox_inches="tight")
