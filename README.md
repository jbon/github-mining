## About this repository
Python scripts for investigating open source hardware GitHub repositories

## Contents
* 'goMine.py' 
  * extracts metadata from GitHub API
  * takes a list of project references as input (a CSV where each line is a list of GitHub repository references <owner>/<repoName> affiliated to a project)
  * produces a JSON file with a reference all branches for each project
  * produces a JSON file with all commits of all branches for each project 
* 'goCreateGraphs.py'
  * takes as input a list of JSON files containing all commit information related to a project produced by 'goMine.py'
  * creates for each project the following graphs in GraphML format:
    * a commit graph (as seen in Insights/Network in GitHub)
    * contributor graphs (where each node is a contributor and each edge is the edition of the same file by two contributors), filtered by filetype
    * graphs of all committed file changes (one subgraph per file), filtered by filetype
* 'analysisActivityVolume.py'
  * computes indicators related to activity volume (number of file changes over time for each project)
  * takes as input the graphs of file changes produced by 'goCreateGraphs.py'
* 'analysisActivityDistribution.py'
  * computes indicators related to activity distribution
  * takes as input the contributor graphs produced by 'goCreateGraphs.py'
  * produces a CSV with computed indicators for all considered projects
* 'clustering.py'
  * apply a k-means clustering to the topological indicators computed on the contributor graphs
  * takes as input the computed list of topological indicators produced by 'analysisActivityDistribution.py'
* 'timeStop.py'
  * just a untility to add timestamps in traces

## Instructions 
... are given in the header of each script

## More info
These scripts are developed as part of a French-German interdisciplinary research project “Open! – Methods and tools for community-based product development”. It is jointly funded by the French and German national science agencies ANR (Agence Nationale de la Recherche, grant ANR-15-CE26-0012) and DFG (Deutsche Forschungsgemeinschaft, grant STA 1112/13-1). 
See http://opensourcedesign.cc

## Refer to this work
Cite as: _Jérémy Bonvoisin. (2018, March 27). jbon/github-mining: For Design Science Journal publication (Version v0.1). [doi:10.5281/zenodo.1208379](http://doi.org/10.5281/zenodo.1208379)_
[![DOI](https://zenodo.org/badge/126846013.svg)](https://zenodo.org/badge/latestdoi/126846013)

Results of these scripts have been used in: Bonvoisin, J., Buchert, T., Preidel, M., & Stark, R. (2018). How participative is open source hardware? Insights from online repository mining. Design Science, 4, E19. [doi:10.1017/dsj.2018.15](https://doi.org/10.1017/dsj.2018.15)
