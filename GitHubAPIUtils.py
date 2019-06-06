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

    # https://developer.github.com/v4/explorer/
    # https://developer.github.com/v4/guides/forming-calls/
    # https://developer.github.com/v4/guides/using-the-explorer/
    # https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad
    # https://blog.codeship.com/an-introduction-to-graphql-via-the-github-api/
    # https://github.community/t5/GitHub-API-Development-and/bd-p/api
    # https://developer.github.com/v4/query/
    # https://developer.github.com/v4/guides/intro-to-graphql/
    # https://medium.com/@fabiomolinar/using-githubs-graphql-to-retrieve-a-list-of-repositories-their-commits-and-some-other-stuff-ce2f73432f7


###################################################################################################################
# HEADER
###################################################################################################################

# standard python libraries
import requests
import json

# constants
DEFAULT_PAGINATION_LENGTH = 20

###################################################################################################################
# FUNCTION runAPIQuery
###################################################################################################################    
def run_APIv4_query(query, APIKey): # A simple function to use requests.post to make the API call.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers={"Authorization": "Bearer " + APIKey})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

        
###################################################################################################################
# FUNCTION prettyPrint
###################################################################################################################    
def prettyPrint (uglyJson):
    print(type(uglyJson))
    if type(uglyJson) is list:
        parsed = json.loads(str(uglyJson).replace("'", '"'))
    elif type(uglyJson) is dict:
        parsed = uglyJson
    print(json.dumps(parsed, indent=2, sort_keys=True))
    
###################################################################################################################
# FUNCTION getAllBranches
###################################################################################################################
# Returns the references to all branches and commi histories of a repository
def getAllBranches(repoOwner, repoName, APIKey):
    
    # GraphQL query with a pagination variable
    # investigate TREE and Deployment
    query = '{ \
        repository(name: "' + repoName + '", owner: "' + repoOwner + '") { \
            refs(refPrefix:"refs/heads/", $pagination$) { \
                edges { \
                    node { \
                        id \
                        name \
                        target { \
                            ... on Commit { \
                                history { \
                                    edges { \
                                        node { \
                                            ... on Commit { \
                                                oid \
                                                abbreviatedOid \
                                            } \
                                        } \
                                    } \
                                } \
                            } \
                        } \
                    } \
                    cursor \
                } \
                pageInfo { \
                    hasNextPage \
                } \
            } \
        } \
    }'   

    # get the first page of results from GraphQL API
    queryResults = run_APIv4_query(
        query.replace(
            '$pagination$', 
            'first:'+str(DEFAULT_PAGINATION_LENGTH)
            )
        , APIKey)
  

      # sometimes repository queries return a 404/"not found" error, in those cases we return an empty list
    if queryResults["data"]["repository"]==None :
        return []
    else :
        returnDict = queryResults["data"]["repository"]["refs"]["edges"]
        
        # get the eventual next pages until we reach the last page
        while queryResults["data"]["repository"]["refs"]["pageInfo"]["hasNextPage"] == True:
            queryResults = run_APIv4_query(
                query.replace(
                    '$pagination$', 
                    'first:'+str(DEFAULT_PAGINATION_LENGTH)+'after:"'+queryResults["data"]["repository"]["refs"]["edges"][-1]["cursor"]+'"'
                    )
                , APIKey)
            returnDict += queryResults["data"]["repository"]["refs"]["edges"]
                    
        return returnDict
  

###################################################################################################################
# FUNCTION getAllForks
###################################################################################################################
# Returns the owner name of all recursive forks of a repository
def getAllForks(repoOwner, repoName, APIKey):
    
    # GraphQL query with a pagination variable
    query = '{ \
        repository(name: "' + repoName + '", owner: "' + repoOwner + '") { \
            forks($pagination$) { \
                edges { \
                    node { \
                        owner { \
                            login \
                        } \
                    } \
                    cursor \
                } \
                pageInfo { \
                    hasNextPage \
                } \
            } \
        } \
    }' 

    # get the first page of results from GraphQL API
    queryResults = run_APIv4_query(
        query.replace(
            '$pagination$', 
            'first:'+str(DEFAULT_PAGINATION_LENGTH)
            )
        , APIKey)
    
    # sometimes repository queries return a 404/"not found" error, in those cases we return an error
    if queryResults["data"]["repository"]==None :
        return []
    else :
        forks = queryResults["data"]["repository"]["forks"]["edges"]
        # get the eventual next pages until we reach the last page
        while queryResults["data"]["repository"]["forks"]["pageInfo"]["hasNextPage"] == True:
            queryResults = run_APIv4_query(
                query.replace(
                    '$pagination$', 
                    'first:'+str(DEFAULT_PAGINATION_LENGTH)+'after:"'+queryResults["data"]["repository"]["forks"]["edges"][-1]["cursor"]+'"'
                    )
                , APIKey)
            forks += queryResults["data"]["repository"]["forks"]["edges"]
        # recursive loop to get all forks of all forks
        subforks = []
        for fork in forks:
            subforks += getAllForks(fork["node"]["owner"]["login"], repoName, APIKey)
                 
        return forks + subforks  

###################################################################################################################
# FUNCTION checkRateLimit
###################################################################################################################
#
def checkRateLimit(APIKey):
    
    query = '{ \
        rateLimit { \
            limit \
            cost \
            remaining \
            resetAt \
        } \
    }'

    return run_APIv4_query(query, APIKey)["data"]["rateLimit"]
    
    
###################################################################################################################
# FUNCTION getCommitDetails
###################################################################################################################
# Returns details of a given commit
def getCommitDetails(repoOwner, repoName, sha, GitHubUserName, APIKey):
   
   # uses GitHub API v3 since v4 does not allow to fetch file info, see:
   # https://github.community/t5/GitHub-API-Development-and/GraphQL-API-get-list-of-files-related-to-commit/td-p/24666
   
    query = "https://api.github.com/repos/"+repoOwner+"/"+repoName+"/commits/"+sha
    queryResults = requests.get(query,auth=(GitHubUserName,APIKey))
    deserializedQueryResults = json.loads(queryResults.text)
    
    return deserializedQueryResults