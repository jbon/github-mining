# About this repository
Python scripts for investigating open source hardware GitHub repositories
## Contents
* `goMine.py` 
  * extracts metadata from GitHub API
  * takes a lost of project references as input (a CSV where each line is a list of GitHub repository references <owner>/<repoName> affiliated to a project)
  * produces for each project a JSON file with a reference all branches
  * produces for each project a JSON file with all commits of all branches
* `goCreateGraphs.py`
  * takes as input a list of JSON files containing all commit information related to a project produced by goMine.py
  * creates for each project the following graphs in GraphML:
    * a commit graph (as seen in Insights/Network in GitHub)
    * contributor graphs (where each node is a contributor and each edge is the edition of the same file by two contributors), filtered per filetype
    * graphs of all committed file changes (one subgraph per file), filtered per filetype
* `analysisActivityVolume.py`
  * computes indicators related to activity volume (number of file changes over time and per project)
  * takes as input the graphs of file changes produced by goCreateGraphs.py
* `analysisActivityDistribution.py`
  * computes indicators related to activity distribution
  * takes as input the contributor graphs produced by goCreateGraphs.py
  * produces a CSV with computed indicators for all considered projects
* `clustering.py`
  * apply a k-means clustering to the topological indicators computed on the contributor graphs
  * takes as input the computed list of topological indicators produced by analysisActivityDistribution.py
* `timeStop.py`
  * just an untility to add timestamps in traces
## Instructions 
... are given in the header of each script
# More info
These scripts are developped as part of a French-German interdisciplinary research project “Open! – Methods and tools for community-based product development”. It is jointly funded by the French and German national science agencies ANR (Agence Nationale de la Recherche, grant ANR-15-CE26-0012) and DFG (Deutsche Forschungsgemeinschaft, grant STA 1112/13-1). 
See http://opensourcedesign.cc
