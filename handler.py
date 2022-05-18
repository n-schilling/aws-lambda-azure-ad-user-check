import os
import urllib3
import json
import logging
import sys
import os
import urllib.parse


urllib3.disable_warnings()

FORMAT = "[%(levelname)s] %(message)s\n"
logger = logging.getLogger()
for h in logger.handlers:
  h.setFormatter(logging.Formatter(FORMAT))
logger.setLevel(logging.INFO)

http_pool = urllib3.PoolManager()


def get_api_token(azure_auth_client_id: str, azure_auth_client_secret: str, azure_tenant_id: str) -> str:
    """Gets an JWT token based on the given credentials for a given resource scope (the API url you want to use for your requests)

    Args:
        azure_auth_client_id (str): Azure app registration id used to authenticate (NOT id of the client secret)
        azure_auth_client_secret (str): Azure app registration client secret secret
        azure_tenant_id (str): Azure tenant id you want to work with
    Returns:
        str: A valid JWT token
    """
    azure_auth_login_url = "https://login.microsoftonline.com/"
    resource_scope       = "https://graph.microsoft.com/"
    logger.info('Start getting Microsoft Azure AD login token')
    payload = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": azure_auth_client_id,
        "client_secret": azure_auth_client_secret,
        "resource": resource_scope
    })
    
    post_response = http_pool.request('POST', azure_auth_login_url + '/' + azure_tenant_id + '/oauth2/token', headers={'Content-Type': 'application/x-www-form-urlencoded'}, body=payload)
    if (post_response.status) != 200:
        logger.error(f"HTTP Call was not okay. HTTP Status: {post_response.status}")
        logger.error(f"Headers are: {post_response.headers}")
        logger.error(f"Body is: {post_response.data.decode('utf-8')}")
        sys.exit(1)
    decoded_response = json.loads(post_response.data.decode('utf-8'))
    login_token = decoded_response['access_token']
    return login_token

def get_azure_ad_user_attributes_by_a_give_attribute(search_attribute: str, search_value: str,  attributes_to_get: list, microsoft_graph_api_token: str) -> list:
    """Getting users with given attributes from Azure AD for given search criteria

    Args:
        search_attribute (str): a valid key to search a user by (mail, userPrincipalName, id)
        search_value (str): The value to search_attribute
        attributes_to_get (list): user attributes to retrieve from data set
        microsoft_graph_api_token (str): A valid Microsoft Graph API Token

    Returns:
        list: list with a dict per user with requested user attributes for given search criteria
    """
    content_type            = 'application/json'
    authorization_type      = 'Bearer ' #this blank in the end is on purpose
    microsoft_graph_api_url = "https://graph.microsoft.com/"
    logger.info(f"Getting users with attributes from Azure AD for attribute {search_attribute} with value {search_value}")
    default_headers = { 'Content-Type': content_type, 'Authorization': authorization_type + microsoft_graph_api_token}
    my_headers = urllib3.util.make_headers()
    my_headers.update(default_headers)

    url_parameter = ','.join(attributes_to_get)
    
    get_response = http_pool.request('GET', microsoft_graph_api_url + "/v1.0/users?$filter=startswith("+ search_attribute +",'"+ search_value + "')&$select=" + url_parameter, headers=my_headers)
    if (get_response.status) != 200:
        logger.error(f"HTTP Call to get user attributes was not okay. HTTP Status: {get_response.status}")
        logger.error(f"Headers are: {get_response.headers}")
        logger.error(f"Body is: {get_response.data.decode('utf-8')}")
        sys.exit(1)
    decoded_response = json.loads(get_response.data.decode('utf-8'))
    return decoded_response['value']


def main(event, context):
    try:
        user_to_search = event['username']
    except:
        logger.error("No event with parameter 'username' provided")
        sys.exit(1)       
    try:
        azure_auth_client_id     = os.environ['AZURE_AUTH_CLIENT_ID']
        azure_auth_client_secret = os.environ['AZURE_AUTH_CLIENT_SECRET']
        azure_tenant_id          = os.environ['AZURE_TENANT_ID']
    except:
        logger.error("Please set MICROSOFT_API_CREDENTIALS as env variables")
        sys.exit(1)
    microsoft_graph_api_token = get_api_token(azure_auth_client_id, azure_auth_client_secret, azure_tenant_id)
    user_data = get_azure_ad_user_attributes_by_a_give_attribute("mail", user_to_search, ['id', 'accountEnabled'], microsoft_graph_api_token)
    user_count = 0
    for user in user_data:
        if user['accountEnabled']:
            user_count += 1
    if user_count == 0:
        logger.info(f"The AzureAD DOES NOT contain an active user with the email {user_to_search}")
    else:
        logger.info(f"The AzureAD contains {len(user_data)} active user with the email {user_to_search}")


if __name__ == "__main__":
    main(0, 0)