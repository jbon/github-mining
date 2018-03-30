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
#   . MatPlotLib (https://matplotlib.org/)
#   . Numpy (http://www.numpy.org)
#   . Pandas (https://pandas.pydata.org)
# -  goprocess() function -> convert json files to graphsML files
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
import pdb
from getopt import getopt, GetoptError
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter, OrderedDict
from sys import stdout, exit, argv
from datetime import datetime, date
import numpy as np
import pandas

#############################################################################################
# FUNCTION help
#############################################################################################

def help():
    print('Required Arguments:')
    print('-i     --input     <path>    path of the directory where the GraphML files are stored')
    print('-o     --output     <path>   path of the directory where the figures should be stored')
    print('Optional Arguments:')
    print('-h     --help                calls help function')
    exit()    
    
#############################################################################################
# FUNCTION exportCSV
#############################################################################################
# write a CSV file containing the two columns given in parameters (X, Y)
def exportCSV(filename, x_col, y_col):
    with open(filename, 'w', newline='') as csvOutput:
        CSVWriter = csv.writer(csvOutput, delimiter=';')
        for x, y in zip(x_col, y_col):
            CSVWriter.writerow([x, y])

#############################################################################################
# FUNCTION loadGraphMLs
#############################################################################################
def loadGraphMLs(inputDir, extension):            

    graphs = []
    projectNames = []
    GraphMLFiles = [f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, f)) and f.lower().endswith(extension)]
    numberOfGraphMLFiles = len(GraphMLFiles)
    print(str(numberOfGraphMLFiles) + ' files found ending with "' + extension + '"')
    for file,i in zip(GraphMLFiles,range(0,len(GraphMLFiles))):
        graphs.append(nx.read_graphml(os.path.join(inputDir, file)))
        projectNames.append(os.path.splitext(os.path.splitext(os.path.splitext(file)[0])[0])[0])
        # processbar
        stdout.write('\r')
        stdout.write("[%-30s] %d%%" % ('=' * int(i*30/len(GraphMLFiles)+1),  i*100/len(GraphMLFiles)+1))
        stdout.flush()
    print('\r')
    return projectNames, graphs
            
#############################################################################################
# FUNCTION commits_time
#############################################################################################

def filechanges_time(fileGraphs, seriesName):

    # initialisation of containers
    dates = [] # for all filechange dates of all projects
    projectIndexes = [] # for identifying to which project the filechange date belongs
    initialFilechanges = OrderedDict() # for the first filechange date of each project
    projectIndex = 0 # to be used in the following for-loop
    
    for fileGraph in fileGraphs:

        # flatten the graph for easier parsing
        filechangeGraph_As_a_List = list(fileGraph.nodes(data=True)) # data=True returns a two-tuple of node and node data dictionary
        initial_filechange = None

        # parse the list of filechanges, insert the corresponding date in "dates" and the project index in "projectIndexes"
        for filechange in filechangeGraph_As_a_List:
            date = datetime.strptime(filechange[1]['date'], '%Y-%m-%dT%H:%M:%SZ').date()
            dates.append(date)
            projectIndexes.append(projectIndex)
            if initial_filechange == None:
                initial_filechange = date
            elif initial_filechange > date:
                initial_filechange = date
        
        if initial_filechange == None:
            print ("error : graph #"+str(projectIndex)+ " ignored because empty")
        else:
            initialFilechanges[projectIndex]=initial_filechange
            projectIndex += 1
            
        
    # get arrangement keys for sorting the projects per date of first file change
    sortedProjectIndexes = sorted(initialFilechanges, key=initialFilechanges.__getitem__)
    sortingKeys = []  
    for i in range(0,len(sortedProjectIndexes)):
        sortingKeys.append(sortedProjectIndexes.index(i))

    # sort the projects per date of first file change
    for i in range(0,len(projectIndexes)):
        projectIndexes[i] = sortingKeys[projectIndexes[i]]
    
    
    ## TIMELINE PLOT (filechanges) ##############################################################
    #############################################################################################

    # use the Pandas library to compute the number of filechanges per quarter
    pandasTimeSeries = pandas.DataFrame([1 for col in dates], dates).set_index(pandas.DatetimeIndex(dates))
    totalCurve = pandasTimeSeries.resample('1M').count()
    #rollingMean = pandas.rolling_mean(totalCurve, window=6)
    rollingMean = totalCurve.rolling(window=12,center=False).mean()

    # initialize fontsizes in matplotlib
    matplotlib.rcParams.update({'font.size': 20})

    # create figure and axes objects
    fig, ax1 = plt.subplots(figsize=(12, 10))

    # duplicate the axes to display two plots in one graph with two different y-axes
    ax2 = ax1.twinx()

    # 1st plot - scatter plot: 1 point per filechange
    ax1.scatter(dates, projectIndexes, c = '#000000',
               marker='8', s=1)
    ax1.set_ylabel('Repositories')
    ax1.set_xlabel('Date')
    #ax1.set_title('Distribution of file changes over time, per repository and in all')

    # 2nd plot - plot: number of filechanges per quarter
    ax2.plot(totalCurve, color='#145F64', alpha=1, linewidth=3.0)
    ax2.plot(rollingMean, color='#FF6600', alpha=1, linewidth=3.0)
    ax2.set_ylabel('Number of file changes per quarter (in all repositories)')
    ax2.set_ylim([0,7500])

    # save figure and data in output folder
    plt.savefig(os.path.join(outputDir, 'filechanges_over_time.'+seriesName+'.pdf'), bbox_inches="tight")
    plt.savefig(os.path.join(outputDir, 'filechanges_over_time.'+seriesName+'.png'), dpi = 300, bbox_inches="tight")
    plt.savefig(os.path.join(outputDir, 'filechanges_over_time.'+seriesName+'.svg'), dpi = 300, bbox_inches="tight")
    exportCSV(os.path.join(outputDir, 'filechanges_over_time.'+seriesName+'.csv'), dates, projectIndexes)

#############################################################################################
# FUNCTION filechanges
#############################################################################################

def filechanges_per_project(projectNames, fileGraphs, seriesName):

    numberOfFileChanges = []
    for fileGraph in fileGraphs:
        numberOfFileChanges.append(fileGraph.number_of_nodes())
    exportCSV(os.path.join(outputDir, 'filechanges_per_project.'+seriesName+'.csv'), projectNames, numberOfFileChanges)

    ## Box PLOT  ################################################################################
    #############################################################################################
    # notched plot
    plt.figure(figsize=(2,7))
    bplot = plt.boxplot(numberOfFileChanges,vert=True, patch_artist=True)

    for patch in bplot['boxes']:
        patch.set_facecolor('#b4b4b4')
    for median in bplot['medians']:
        median.set(color='k')

    ax = plt.gca()
    ax.set_ylabel('Number of commits')
    ax.get_xaxis().set_ticks([])
    ax.set_ylim([0,10000])
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.savefig(os.path.join(outputDir, 'filechanges_per_project.'+seriesName+'.boxplot.svg'), bbox_inches="tight")

	
###################################################################################################################
# BODY
###################################################################################################################

# declare global variables
global inputDir, outputDir

# get command line arguments
try:
    options, remainder = getopt(argv[1:], 'i:o:rdch', ['input=', 'output=','rewrite','delete', 'clearscreen', 'help'])
except GetoptError as err:
    print(str(err))
    exit(2)
    
# initialise the parameters to be found in the arguments
inputDir = ''
outputDir = ''
rewrite = False
delete = False
clearscreen = False

# search the parameters in the arguments given to the script
for option, argument in options:
    if option in ('-i','--input'):
        inputDir = argument
    elif option in ('-o','--output'):
        outputDir = os.path.relpath(argument)
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

#load required graphs
projectNames, fileGraphs_ALL = loadGraphMLs(inputDir, '.filechanges.all.graphml') 
_, fileGraphs_PHW = loadGraphMLs(inputDir, '.filechanges.phw.graphml') 
_, fileGraphs_CHW = loadGraphMLs(inputDir, '.filechanges.chw.graphml') 

print ("build distribution of filechanges over time - CHW")
filechanges_time(fileGraphs_CHW, "CHW")
filechanges_per_project(projectNames, fileGraphs_CHW, "CHW")
print ("build distribution of filechanges over time - PHW")
filechanges_time(fileGraphs_PHW, "PHW")
filechanges_per_project(projectNames, fileGraphs_PHW, "PHW")
print ("build distribution of filechanges over time - ALL")
filechanges_time(fileGraphs_ALL, "ALL")
filechanges_per_project(projectNames, fileGraphs_ALL, "ALL")

