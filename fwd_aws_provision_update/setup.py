"""Functions to create read-only IAM roles and policies in all accounts.

IAM role and policy that provide read-only access are created in every account
of organization. If some role or policy already exist then its creation is
skipped. List of ARNs for read-only roles in all accounts are written into
JSON file in the current system folder.

    Functions:
        setup_account(account)
        setup(trusted_account, external_id, credentials_p, mgmt_account_p)
"""

from functions import *
import re
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError

def setup_account(account_id):
    """Work on processing account in a thread.

    Account is checked for existence of read-only policy and role. If the
    policy or role do not exist then they are created. Results of processing of
    policy and role in each account are sent to stdout.

    If the processed account is management account in the organization then we
    use credentials of the user under which this script is run, otherwise we
    use switching to role OrganizationAccountAccessRole that exist by default
    in every account of organization except management account.

        Parameters:
            account : str
                ID of account to be checked

        Returns:
            None
    """
    global current_user_credentials, mgmt_account, trusted_account, external_id

    # set credentials to access account
    if not account_id == mgmt_account:
        credentials = switch_roles(account_id, current_user_credentials)
    else:
        credentials = current_user_credentials

    # check if read-only policy exists, create if absent
    if check_managed_policy(
        FWD_READ_ONLY_POLICY_NAME,
        credentials
    ):
        print('Read-only policy exists in account', account_id)
    else:
        create_policy(
            FWD_READ_ONLY_POLICY_NAME,
            FWD_READ_ONLY_POLICY_DOCUMENT,
            credentials
        )
        print('Read-only policy created in account', account_id)

    # check if read-only role exists, create if absent
    if check_role(
        FWD_READ_ONLY_ROLE_NAME,
        credentials
    ):
        print('Read-only role   exists in account', account_id)
    else:
        if external_id == None:
            document = re.sub('###TRUSTED ACCOUNT ID###',
                              trusted_account,
                              FWD_ASSUME_ROLE_POLICY_DOCUMENT)
        else:
            document = re.sub('###EXTERNAL ID###',
                              external_id,
                              FWD_ASSUME_ROLE_POLICY_DOCUMENT_EXTERNAL_ID)
        create_role(
            FWD_READ_ONLY_ROLE_NAME,
            document,
            FWD_READ_ONLY_POLICY_NAME,
            credentials
        )
        print('Read-only role   created in account', account_id)

def setup(trusted_account_p, external_id_p, credentials_p, mgmt_account_p):
    """Create read-only IAM roles and policies in all accounts.

    List of accounts is fetched from organization and then each account is
    processed separately. For better performance accounts are processed in
    concurrent threads. When each thread is started the total number of active
    threads is checked. If the number of threads reaches the limit then start
    of the next thread is postponed. The limit for the number of concurrent
    threads is defined as the number of CPU cores available in the system.

    When read-only role is created or found in account its ARN is added to an
    array which is written to JSON file after all accounts are processed.

        Parameters:
            trusted_account : str
                ID of account that is trusted with read-only access to all
                accounts in the organization
            external_id : str
                external ID that is used to access accounts of organization
                from account that does not belong to this organization
            credentials_p: dict
                current user credentials
            mgmt_account_p : str
                ID of management account

        Returns:
            None
    """

    global current_user_credentials, mgmt_account, trusted_account, external_id
    current_user_credentials = credentials_p
    mgmt_account = mgmt_account_p
    trusted_account = trusted_account_p
    external_id = external_id_p

    # list accounts in organization
    accounts = list_accounts(current_user_credentials)

    # prepare data to output into file
    all_accounts_data_dict = {}

    for account in accounts:
        account_data = {}
        account_data['accountId'] = account['id']
        account_data['accountName'] = account['name']
        account_data['externalId'] = external_id

        all_accounts_data_dict[account['id']] = account_data

    # perform setup in all accounts
    pool = ThreadPoolExecutor(max_workers = None)
    threads = {
            pool.submit(setup_account, account): account
        for account in list(all_accounts_data_dict.keys())
    }
    for t in threads:
        account = threads[t]
        try:
            t.result()
        except ClientError as setup_error:
            all_accounts_data_dict[account]['enabled'] = \
                setup_error.response['Error']['Message']
            all_accounts_data_dict[account]['enabled'] = None
            print(setup_error.response['Error']['Message'])
            continue
        else:
            all_accounts_data_dict[account]['enabled'] = True
            all_accounts_data_dict[account]['roleArn'] = "arn:aws:iam::" + account + ":role/" \
                                                         + FWD_READ_ONLY_ROLE_NAME

    # write accounts data into file
    awsregions = {}
    
    with open(REGIONS) as file:
        for line in file:
            key = line.strip()
            awsregions[key] = int(time.time())

    with open(APPCREDS) as creds:
        auth = creds.read().splitlines()

    proxyurl = "https://" + APPHOST + "/api/networks/" + NETWORKID + "/proxy"
    
    response = requests.get(proxyurl, auth=(auth[0], auth[1]))

    proxy_dict = response.json()

    json_dict = {
                'name' : SETUPID,
                'type' : 'AWS',
                'collect' : True,
                'assumeRoleInfos': list(all_accounts_data_dict.values()),
                'regions' : awsregions
                }
    if proxy_dict is not None:
        print('There is a Proxy')
        print(proxy_dict)
        json_dict['proxyServerId'] = proxy_dict['id']
    else:
        print('There is no Proxy')
    all_accounts_data = list(all_accounts_data_dict.values())
    all_accounts_data_string = json.dumps(json_dict)
    output_file = open(OUTPUT_FILENAME, 'w')
    output_file.write(json.dumps(json.loads(all_accounts_data_string),
                                 indent=4,
                                 sort_keys=False))
    output_file.close()

    url = "https://" + APPHOST + "/api/networks/" + NETWORKID + "/cloudAccounts"
    urldelete = "https://" + APPHOST + "/api/networks/" + NETWORKID + "/cloudAccounts/" + SETUPID
    data = open('fwd_accounts_data.json', 'rb')
    d = requests.delete(urldelete, auth=(auth[0], auth[1]))
    r = requests.post(url, auth=(auth[0], auth[1]), json=json_dict)

    print(d.status_code) 

    print(r.status_code) 

