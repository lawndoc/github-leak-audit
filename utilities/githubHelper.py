from time import sleep
from config import Config
from github import Github, GithubException, GithubIntegration, Installation, Consts, RateLimitExceededException
import requests


class MyGithubIntegration(GithubIntegration):
    def __init__(self, app_id, private_key):
        """
        GithubIntegration extension that supports the *user* app installation API.
        """
        super().__init__(app_id, private_key)

    def get_user_installation(self, username):
        """
        :calls: `GET /users/{username}/installation <https://docs.github.com/en/rest/reference/apps#get-a-user-installation-for-the-authenticated-app>`_
        :param username: str
        :rtype: :class:`github.Installation.Installation`
        """
        headers = {
            "Authorization": f"Bearer {self.create_jwt()}",
            "Accept": Consts.mediaTypeIntegrationPreview,
            "User-Agent": "PyGithub/Python",
        }

        response = requests.get(
            f"{self.base_url}/users/{username}/installation",
            headers=headers,
        )
        response_dict = response.json()
        return Installation.Installation(None, headers, response_dict, True)


class GithubHelper:
    def __init__(self):
        """
        Helper class to abstract interactions with the GitHub API.
        """
        self.authToken = self.generateToken()

    def enumerateMembers(self):
        """
        Enumerate the members of the GitHub organization
        """
        url = 'https://api.github.com/graphql'
        headers = {"Authorization": f"token {self.authToken}"}
        hasNextPage = True
        cursor = ""
        members = []
        while hasNextPage:
            query = { 'query' : """
            {
                organization(login: \"""" + Config.ORG_NAME + """\") {
                    membersWithRole(first: 100""" + (f", after: \"{cursor}\"" if cursor else '') + """) {
                    totalCount
                    nodes {
                        login
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    }
                }
            }
            """}
            response = requests.post(url=url, json=query, headers=headers)
            members += [member["login"] for member in response.json()["data"]["organization"]["membersWithRole"]["nodes"]]
            hasNextPage = response.json()["data"]["organization"]["membersWithRole"]["pageInfo"]["hasNextPage"]
            if hasNextPage:
                cursor = response.json()["data"]["organization"]["membersWithRole"]["pageInfo"]["endCursor"]
        return members

    def buildLeakQueries(self, members):
        """
        Build search queries that are not longer than the maximum length accepted by GitHub.
        Must be 256 characters not including operators or qualifiers.
        """
        queries = [f"{Config.ORG_NICKNAME.lower()} user:"]
        userGroups = [[]]
        groupLen = len(Config.ORG_NICKNAME)
        for member in members:
            if len(member) + groupLen >= 256:
                # add current group to queries and start new one
                queries[-1] += " user:".join(userGroups[-1])
                queries.append(f"{Config.ORG_NICKNAME.lower()} user:")
                userGroups.append([])
                groupLen = len(Config.ORG_NICKNAME)
            # user fits in current group
            userGroups[-1].append(member)
            groupLen += len(member)
        # add remaining users group to final query
        queries[-1] += " user:".join(userGroups[-1])
        return queries
    
    
    def leakSearch(self, queries):
        """
        Search for references to the organization in members' personal repos.
        Includes exponential backoff for rate limiting.
        """
        gh = Github(self.authToken)
        allHits = []
        for query in queries:
            print("Trying query -> " + query)
            delayTime = 1
            while delayTime <= 128:
                try:
                    codeHits = [hit.repository.full_name for hit in gh.search_code(query=query)]
                    repoHits = [hit.full_name for hit in gh.search_repositories(query=query)]
                    allHits += [repo for repo in codeHits + repoHits if repo not in Config.EXCEPTIONS]
                    break
                except (RateLimitExceededException, GithubException) as e:
                    errorMsg = e.data["errors"][0]["message"]
                    if errorMsg == "The listed users and repositories cannot be searched either because \
                    the resources do not exist or you do not have permission to view them.":
                        # no user in this query group has any public repos (somehow)
                        break
                    elif e.status == 403:
                        # hit rate limit; sleep and try again; double next sleep time
                        print(f"Rate limit exceeded. Waiting {delayTime} seconds before trying again...")
                        sleep(delayTime)
                        delayTime *= 2
                    else:
                        raise e
            else:
                # reached max delay time
                print("ERROR: Max delay time reached; skipping query")
        # deduplicate repos that matched both name and code search
        return set(allHits)

    def generateToken(self):
        """
        Generate an access token for the GitHub App or fetch the given PAT.
        """
        if Config.AUTH_TYPE == "APP":
            integration = MyGithubIntegration(Config.APP_ID, Config.PRIVATE_KEY)
            install = integration.get_user_installation(Config.ORG_NAME)
            access = integration.get_access_token(install.id)
            return access.token
        else:
            return Config.PAT
