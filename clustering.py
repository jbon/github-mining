#############################################################################################
# SCRIPT INFORMATION
#############################################################################################

# LICENSE INFORMATION:
# ---------------------
# clustering.py 
# Authors: Jérémy Bonvoisin, Jonas Massmann
# Homepage: http://opensourcedesign.cc
# License: GPL v.3

# PREREQUISITES:
# ---------------
# - a CSV file with:
#    . no header
#    . first column = project name
# - non standard libraries (install with <libraryName>):
#   . sklearn (http://scikit-learn.org)
#   . scipy (required by sklearn)
#
# ARGUMENTS:
# -----------
# see help() function

#############################################################################################
# HEADER
#############################################################################################

import os
import csv
import pdb
import scipy
from getopt import getopt, GetoptError
from sys import stdout, exit, argv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn import datasets
from collections import Counter

#############################################################################################
# FUNCTION help
#############################################################################################

def help():
    print('Required Arguments:')
    print('-i     --input     <path>    path of the input CSV file')
    print('Optional Arguments:')
    print('-p     --preview             shows only the results but does not save them')
    print('-h     --help                calls help function')
    exit()    

###################################################################################################################
# BODY
###################################################################################################################

#initialisation
#####################
try:
    options, remainder = getopt(argv[1:], 'i:ph', ['input=', 'help'])
except GetoptError as err:
    print(str(err))
    exit(2)
    
# initialise the parameters to be found in the arguments
CSVInputFile = ''
previewmode = False
# search the parameters in the arguments given to the script
for option, argument in options:
    if option in ('-i','--input'):
        CSVInputFile = argument
    elif option in ("-p", "--preview"):
        previewmode = True
    elif option in ("-h", "--help"):
        help()
       
# check whether all required parameters have been given as arguments and if not throw exception and abort
if CSVInputFile == '':
    print("Argument required: input CSV file. Type '-i <file path>' in the command line")
    exit(2)
if not os.path.exists(CSVInputFile) or not os.access(CSVInputFile, os.R_OK):
    print("File '"+CSVInputFile+"' does not seem to exist or is not accessible. Check the file path and your access rights")
    exit(2)

if not previewmode:
    CSVInputFileName = os.path.splitext(CSVInputFile)[0]
    CSVOutputFile_Data = os.path.join (CSVInputFileName + ".clustered.csv")
    CSVOutputFile_Centers = os.path.join (CSVInputFileName + ".centers.csv")
    CSVOutputFile_NearestDataPoints = os.path.join (CSVInputFileName + ".nearestDataPoints.csv")

# Load CSV file 
#####################
data = []
projectNames = []
with open(CSVInputFile, newline='') as csvInput:
    CSVReader = csv.reader(csvInput, delimiter=';')
    for row in CSVReader:
        projectNames.append(row[0])
        for i in range(1, len(row)):
            row[i]= float(row[i])
            if row[i] != row[i]: # meaning row[i] is NaN
                row[i] = 0
        data.append(row[1:5])
		# row 0 gets number of committers
		# row 1 gets completeness
		# row 2 gets centrality index
		# row 3 gets clustering index
data = np.array(data)
# normalize the number of committers 
data[:,0] = data[:,0]/data[:,0].max()
# get rid of completeness 
data = np.delete(data, (1), axis=1)
print (data)
print("\n")
'''
# Elbow method to determine the ideal number of clusters
#####################
distorsions = []
for k in range(2, 20):
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(data)
    distorsions.append(kmeans.inertia_)

fig = plt.figure(figsize=(15, 5))
plt.plot(range(2, 20), distorsions)
plt.grid(True)
plt.title('Elbow curve')    
plt.show()
'''
# K-means computation
#####################
numberOfClusters = 4
kmeans = KMeans(n_clusters=numberOfClusters)
kmeans.fit(data)
clusterAffiliation = kmeans.labels_
clusterCenters = kmeans.cluster_centers_ 
clusterCentersAsNp = np.array(clusterCenters)
# find the data point which is at the nearest to each center
nameNearestDataPoints = [None] * numberOfClusters
coordinatesNearestDataPoints = [None] * numberOfClusters
for c in range(0,len(clusterCenters)):
    center = clusterCenters[c]
    minDistance = 1
    for d in range(0,len(data)):
        distanceToCenter = scipy.spatial.distance.euclidean(data[d], center)
        if distanceToCenter < minDistance:
            minDistance = distanceToCenter
            coordinatesNearestDataPoints[c] = data[d]
            nameNearestDataPoints[c] = projectNames[d]
coordinatesNearestDataPoints = np.array(coordinatesNearestDataPoints)
numberOfPointsPerCluster = Counter(clusterAffiliation)
print(clusterCenters)
print(nameNearestDataPoints)
print(coordinatesNearestDataPoints)
print(numberOfPointsPerCluster)

# 3D Plot
#####################
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='3d')
colors = ['black','purple','orangered','chartreuse','blue', 'turquoise'] # should be of size numberOfClusters
colors = colors[0:numberOfClusters]
legendHandles = [] 
# plot the clusters
for c in range(0,numberOfClusters): # there may be a more pythonic way of slicing the dataset per cluster ...
    membersOfThisCluster = []
    for d in range(0,len(data)): 
        if clusterAffiliation[d] == c :
            membersOfThisCluster.append(data[d])
    membersOfThisCluster = np.array(membersOfThisCluster)
    legendHandles.append(ax.scatter(membersOfThisCluster[:,0],membersOfThisCluster[:,1],membersOfThisCluster[:,2],color=colors[c], marker= '.', s=200, alpha=.3, label='C'+str(c)+': '+str(numberOfPointsPerCluster[c])+' projects'))
# plot the clusters centers and nearest dataPoints
ax.scatter(clusterCenters[:,0],clusterCenters[:,1],clusterCenters[:,2], color=colors, marker= 'x', s=40)
ax.scatter(coordinatesNearestDataPoints[:,0],coordinatesNearestDataPoints[:,1],coordinatesNearestDataPoints[:,2], color=colors, marker= '.', s=20)

ax.set_xlabel('number of committers')
ax.set_ylabel('centrality index')
ax.set_zlabel('clustering index')
ax.view_init(azim=-45, elev=30)
if previewmode:
    plt.legend(handles=legendHandles)
    plt.show()
else:
    plt.savefig(os.path.join (CSVInputFileName + ".pdf"))
    plt.savefig(os.path.join (CSVInputFileName + ".png"))
    plt.savefig(os.path.join (CSVInputFileName + ".svg"))

# write CSV file with results
#####################
if not previewmode:
    outputData = np.concatenate((list(zip(projectNames, clusterAffiliation)), data), axis=1)
    with open(CSVOutputFile_Data,'w', newline='') as csvOutput:
            CSVWriter = csv.writer(csvOutput, delimiter=";")
            for row in outputData:
                CSVWriter.writerow(row)
    with open(CSVOutputFile_Centers,'w', newline='') as csvOutput:
            CSVWriter = csv.writer(csvOutput, delimiter=";")
            for row in clusterCenters:
                CSVWriter.writerow(row)
    with open(CSVOutputFile_NearestDataPoints,'w', newline='') as csvOutput:
            CSVWriter = csv.writer(csvOutput, delimiter=";")
            for row in zip(nameNearestDataPoints, coordinatesNearestDataPoints):
                CSVWriter.writerow(row)