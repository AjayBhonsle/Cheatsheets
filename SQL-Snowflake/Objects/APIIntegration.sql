-- 1. Create a secret to store your Git access token
CREATE OR REPLACE SECRET git_pat_secret
  TYPE = PASSWORD
  USERNAME = ''
  PASSWORD = ''; #access token

-- 2. Create the API Integration for Git
CREATE OR REPLACE API INTEGRATION git_api_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/USER')
  ALLOWED_AUTHENTICATION_SECRETS = (git_pat_secret)
  ENABLED = TRUE;

-- 3. Create the Snowflake Git Repository stage
CREATE OR REPLACE GIT REPOSITORY my_git_repo
  API_INTEGRATION = git_api_integration
  GIT_CREDENTIALS = git_pat_secret
  ORIGIN = 'https://github.com/your_org_or_user/your_repo.git';