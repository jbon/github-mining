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
#   . scipy (required for sklearn)
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
from getopt import getopt, GetoptError
from sys import stdout, exit, argv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn import datasets

#############################################################################################
# FUNCTION help
#############################################################################################

def help():
    print('Required Arguments:')
    print('-i     --input     <path>    path of the input CSV file')
    print('Optional Arguments:')
    print('-h     --help                calls help function')
    exit()    

###################################################################################################################
# BODY
###################################################################################################################

#initialisation
#####################
try:
    options, remainder = getopt(argv[1:], 'i:h', ['input=', 'help'])
except GetoptError as err:
    print(str(err))
    exit(2)
    
# initialise the parameters to be found in the arguments
CSVInputFile = ''

# search the parameters in the arguments given to the script
for option, argument in options:
    if option in ('-i','--input'):
        CSVInputFile = argument
    elif option in ("-h", "--help"):
        help()
       
# check whether all required parameters have been given as arguments and if not throw exception and abort
if CSVInputFile == '':
    print("Argument required: input CSV file. Type '-i <file path>' in the command line")
    exit(2)
CSVOutputFile_Data = os.path.join (os.path.splitext(CSVInputFile)[0] + ".clustered.csv")
CSVOutputFile_Centers = os.path.join (os.path.splitext(CSVInputFile)[0] + ".centers.csv")

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
        data.append(row[2:5])
data = np.array(data)
#print (data)
#print("\n")

# Elbow method to determine the ideal number of clusters
#####################
# distorsions = []
# for k in range(2, 20):
    # kmeans = KMeans(n_clusters=k)
    # kmeans.fit(data)
    # distorsions.append(kmeans.inertia_)

# fig = plt.figure(figsize=(15, 5))
# plt.plot(range(2, 20), distorsions)
# plt.grid(True)
# plt.title('Elbow curve')    
# plt.show()

# K-means computation
#####################
kmeans = KMeans(n_clusters=6)
kmeans.fit(data)
clusterAffiliation = kmeans.labels_
clusterCenters = kmeans.cluster_centers_ 
#print(clusterCenters)
from collections import Counter
print(Counter(clusterAffiliation))

# 3D Plot
#####################
fig = plt.figure(figsize=(15, 5))
ax = fig.add_subplot(111, projection='3d')

colors = ['b','g','r','c','m','y']
c = [colors[k] for k in clusterAffiliation]
ax.scatter(data[:,0],data[:,1],data[:,2],color=c, s=5)

ax.set_xlabel('completeness')
ax.set_ylabel('centralization_index')
ax.set_zlabel('network_clustering')
plt.show()

# write CSV file with results
#####################
outputData = np.concatenate ((list(zip(projectNames, clusterAffiliation)), data), axis=1)
with open(CSVOutputFile_Data,'w', newline='') as csvOutput:
        CSVWriter = csv.writer(csvOutput, delimiter=";")
        for row in outputData:
            CSVWriter.writerow(row)
with open(CSVOutputFile_Centers,'w', newline='') as csvOutput:
        CSVWriter = csv.writer(csvOutput, delimiter=";")
        for row in clusterCenters:
            CSVWriter.writerow(row)
