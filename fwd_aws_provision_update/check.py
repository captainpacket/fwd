"""Functions to check existence of read-only IAM roles and policies in all accounts.

All accounts are checked for existance of IAM roles and policies that provide
read-only access from trusted account. No other action is taken.

    Functions:
        check_account(account)
        check(credentials_p, mgmt_account_p)
"""

from functions import *
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError

def check_account(account_id):
    """Work on processing account in a thread.

    Account is checked for existence of read-only policy and role and results
    of checks are sent to stdout.

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

    global current_user_credentials, mgmt_account

    # set credentials to access account
    if not account_id == mgmt_account:
        credentials = switch_roles(account_id, current_user_credentials)
    else:
        credentials = current_user_credentials

    # check if read-only role exists
    if check_role(
        FWD_READ_ONLY_ROLE_NAME,
        credentials
    ):
        print('Read-only role   exists in account', account_id)
    else:
        print('Read-only role   does not exist in account', account_id)

    # check if read-only policy exists
    if check_managed_policy(
        FWD_READ_ONLY_POLICY_NAME,
        credentials
    ):
        print('Read-only policy exists in account', account_id)
    else:
        print('Read-only policy does not exist in account', account_id)

def check(credentials_p, mgmt_account_p):
    """Check existence of read-only IAM roles and policies in all accounts.

    List of accounts is fetched from organization and then each account is
    processed separately. For better performance accounts are processed in
    concurrent threads. When each thread is started the total number of active
    threads is checked. If the number of threads reaches the limit then start
    of the next thread is postponed. The limit for the number of concurrent
    threads is defined as the number of CPU cores available in the system.

        Parameters:
            credentials_p: dict
                current user credentials
            mgmt_account_p : str
                ID of management account

        Returns:
            None
    """

    global current_user_credentials, mgmt_account
    current_user_credentials = credentials_p
    mgmt_account = mgmt_account_p

    # list accounts in organization
    accounts = list_accounts(current_user_credentials)
    account_ids = []
    for account in accounts:
        account_ids.append(account['id'])

    # perform check in all accounts
    pool = ThreadPoolExecutor(max_workers = None)
    threads = [pool.submit(check_account, account) for account in account_ids]
    for t in threads:
        try:
            t.result()
        except ClientError as setup_error:
            print(setup_error.response['Error']['Message'])
            continue
