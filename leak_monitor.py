#!/usr/bin/env python3
from config import Config
from utilities import GithubHelper
    

def generateReport(leakedRepos) -> dict:
    """
    Generate the HTML report for potentially leaked repos
    """
    report = {"leaks": [], "count": 0}
    for repoName in leakedRepos:
        remediation = f"Investigate <a href='https://github.com/{repoName}'>{repoName}</a> and take it down if it contains {Config.ORG_NICKNAME} information."
        report["leaks"].append({"repo": repoName,
                                "remediation": remediation})
        report["count"] += 1
    return report


if __name__ == "__main__":
    print("""
      _____ _ _   _    _       _                         _ _ _   
     / ____(_) | | |  | |     | |         /\            | (_) |  
    | |  __ _| |_| |__| |_   _| |__      /  \  _   _  __| |_| |_ 
    | | |_ | | __|  __  | | | | '_ \    / /\ \| | | |/ _` | | __|
    | |__| | | |_| |  | | |_| | |_) |  / ____ \ |_| | (_| | | |_ 
     \_____|_|\__|_|  |_|\__,_|_.__/  /_/    \_\__,_|\__,_|_|\__|

    Leak Monitor
    
    Author: C.J. May @lawndoc

    """)
    
    # use GitHub's API to search for leaked code
    gh = GithubHelper()
    print(f"Enumerating '{Config.ORG_NAME}' members...")
    members = gh.enumerateMembers()
    queries = gh.buildLeakQueries(members)
    print(f"Searching for personal repos containing references to {Config.ORG_NICKNAME}...")
    leaks = gh.leakSearch(queries)

    # generate report data from failed checks
    print("Compiling leak monitoring report data...")
    report = generateReport(leaks)
    with open("LeakReport.html", "w+") as f:
        f.write(report)

    print("Done.")
