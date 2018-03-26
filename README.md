# github-mining
GitHub mining scripts for investigating open source hardware repositories
Contents:
* analysisActivityDistribution.py
  * computes indicators related to activity distribution
  * takes contributor graphs as input
  * produces a CSV with computed indicators for all considered projects
* analysisActivityVolume.py
  * computes indicators related to activity volume
  * takes graphs of file changes as inputs
* clustering.py
  * apply a k-means clustering to the topological indicators computed on the contributor graphs
  * takes as input the computed list of topological indicators
* goCreateGraphs.py
  * takes as input a list of JSON files containing commit information
  * creates for each project a commit graph (in GraphML)
  * creates for each project three contributor graphs (in GraphML): the first corresponds to CAD files, the second CAD and hardware related documentation, the third to all files regardless of their type and content
  * creates for each project three graphs of all committed file changes (in GraphML): the first corresponds to CAD files, the second CAD and hardware related documentation, the third to all files regardless of their type and content
* goMine.py : 
  * extracts metadata from GitHub API
  * takes project references as input (a CSV where each line is a list of GitHub repository references <owner>/<repoName>)
  * produces for each project a JSON file with all commits of all branches
  * produces for each project a JSON file with a reference all branches
* timeStop.py
  * just an untility to add timestamps in traces