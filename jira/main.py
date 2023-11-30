import jira

# https://jira.readthedocs.io/
print(jira.__version__)

SERVER = 'https://your_domain.atlassian.net'
ACCOUNT_EMAIL = "your_email@your_domain.com"
API_TOKEN = "your_api_token"
ISSUE_KEY = 'ABC-123'

# Jira Cloud - username:api_token
# https://id.atlassian.com/manage-profile/security/api-tokens
# https://jira.readthedocs.io/examples.html#username-api-token
# https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/
auth_jira = jira.JIRA(
    server=SERVER,
    basic_auth=(
        ACCOUNT_EMAIL,
        API_TOKEN
    )
)

# Self-Hosted (Jira Server/Data Center)
# auth_jira = jira.JIRA(
#     server=SERVER,
#     token_auth=API_TOKEN,
# )

# username:password는 2단계 인증(two-step verification)을 사용하지 않는 경우에만 사용할 수 있다.
# https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
# https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-basic-auth-and-cookie-based-auth/
# auth_jira = jira.JIRA(
#     server=SERVER,
#     basic_auth=(
#         ACCOUNT_EMAIL,
#         'password'
#     )
# )

print(auth_jira.current_user())  # account_id: 62de676f5f7842fb12938220
print(auth_jira.JIRA_BASE_URL)

try:
    # Get issue: https://developer.atlassian.com/cloud/jira/software/rest/api-group-issue/#api-rest-agile-1-0-issue-issueidorkey-get
    issue = auth_jira.issue(ISSUE_KEY)  # 200 OK
    # issue = auth_jira.issue('ABC-123')  # 404 Issue does not exist or you do not have permission to see it
    print(issue.get_field('summary'))
    print(issue.get_field('issuetype'))
except jira.exceptions.JIRAError as ex:
    print(f"status_code: {ex.status_code}")
    print(f"response: {ex.response.text}")
