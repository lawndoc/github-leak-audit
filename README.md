# GitHub Leak Audit

A GitHub workflow that scans your organization members' personal public repos for code that has potentially been leaked from your organization. Usually, this is a simple mistake, but it is currently impossible for organizations to prevent because GitHub doesn't support managed accounts.

When the workflow is done searching for potentially leaked code, it will build a report and email it to the email addresses you specify.

## Setup Instructions

### 1. Fork this Repo

Fork this repo under the ownership of the organization you want to monitor for leaks.

### 2. Set up required secrets

For this app to function, it needs access to your organization's resources in the GitHub API. You have two options for authentication (click each option for setup instructions):

1. [GitHub App creation](https://docs.github.com/en/developers/apps/building-github-apps/creating-a-github-app) ([generate private key](https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps#generating-a-private-key) and [install it in your organization](https://docs.github.com/en/developers/apps/managing-github-apps/installing-github-apps#installing-your-private-github-app-on-your-repository))
2. [Personal Authentication Token (PAT) creation](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-personal-access-token)

For a classic PAT, you will need "read:org" permission. For a GitHub App, you need Organization -> Members -> Read-only permission.

PATs are a little simpler, but creating a GitHub App for your organization is the preferred method for two reasons. First, it has a better rate limit in GitHub's API and is less likely to fail if you have a lot of members. Second, it isn't tied to an individual user account, so you won't run into issues if the individual who sets this up leaves the GitHub organization.

This app also needs email credentials to send the report email. You'll need to provide an SMTP server address as well as credentials for the account that is sending the email.

Below is an overview of the secrets that will need to be set up in your forked repo (including the ones mentioned above). Here is a link to documentation on [how to set up GitHub Actions secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).

| Secret | Description | Required |
| --- | --- | --- |
| APP_ID | The App ID of the GitHub App you created | Y |
| PRIVATE_KEY | The private key of the GitHub App you created | Y |
| PAT | You can use a personal access token (PAT) instead of a GitHub App | N |
| ORG_NAME | Your organization's "username" as it appears on GitHub | Y |
| ORG_NICKNAME | The short name of your organization used to identify potential leaks (ex. microsoft) | Y |
| EMAIL_SERVER | SMTP server address to send the email report | Y |
| EMAIL_USERNAME | Username to authenticate to the SMTP server | Y |
| EMAIL_PASSWORD | Password to authenticate to the SMTP server | Y |

### 3. Enable GitHub Actions workflow

Once the secrets are set up in your forked repo, you'll need to enable the workflow to allow the leak audit to run periodically. By default, forked repos will disable any GitHub Actions. To re-enable them, you can go to the "Actions" tab in your repo and enable workflows.

Once enabled, the leak audit should run every day at 2:30am CST.
