import os


class Config:
    """ GitHub authentication -- needs either a GitHub App
        or a personal access token (PAT).
    """
    # App ID and Private Key of the GitHub app installed in org
    APP_ID = os.environ.get("APP_ID") or ""
    PRIVATE_KEY = os.environ.get("PRIVATE_KEY") or ""
    # Personal Access Token for the bot or user account
    PAT = os.environ.get("PAT") or ""
    # Prefer App over PAT due to rate limits
    AUTH_TYPE = "APP" if APP_ID else "PAT"
    if AUTH_TYPE == "PAT" and not PAT:
        raise ValueError("The app is missing both a GitHub App and a Personal Access Token.")

    """ GitHub organization """
    ORG_NAME = os.environ.get("ORG_NAME") or ""
    ORG_NICKNAME = os.environ.get("ORG_NICKNAME") or ""
    if not (ORG_NAME and ORG_NICKNAME):
        raise ValueError("You must set ORG_NAME and ORG_NICKNAME in config.py")
    
    """ Repos that are exceptions (put false positives here)
        Example:
        EXCEPTIONS = ["lawndoc/github-leak-audit", "lawndoc/seccomp-ci-demo"]
    """
    EXCEPTIONS = []
