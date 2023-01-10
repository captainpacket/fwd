"""Functions to delete read-only IAM roles and policies from all accounts.

All accounts are checked for existance of IAM roles and policies that provide
read-only access from trusted account. All of these roles and policies that
were found will be deleted.

    Functions:
        clear_account(account)
        clear(credentials_p, mgmt_account_p)
"""

from functions import *
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError

def clear_account(account_id):
    """Work on processing account in a thread.

    Account is checked for existence of read-only policy and role. If the
    policy or role exist then they are deleted. Results of processing of
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

    global current_user_credentials, mgmt_account

    # set credentials to access account
    if not account_id == mgmt_account:
        credentials = switch_roles(account_id, current_user_credentials)
    else:
        credentials = current_user_credentials

    # check if read-only role exists, delete if present
    try:
        if check_role(
                FWD_READ_ONLY_ROLE_NAME,
                credentials
        ):
            delete_role(
                FWD_READ_ONLY_ROLE_NAME,
                FWD_READ_ONLY_POLICY_NAME,
                credentials
            )
            print('Read-only role   deleted in account', account_id)
        else:
            print('Read-only role   does not exist in account', account_id)
    except Exception as err:
        raise RuntimeError("Cannot check or delete role")

    # check if read-only policy exists, delete if present
    if check_managed_policy(
            FWD_READ_ONLY_POLICY_NAME,
            credentials
    ):
        delete_policy(
            FWD_READ_ONLY_POLICY_NAME,
            credentials
        )
        print('Read-only policy deleted in account', account_id)
    else:
        print('Read-only policy does not exist in account', account_id)

def clear(credentials_p, mgmt_account_p):
    """Delete read-only IAM roles and policies from all accounts.

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

    # perform clear in all accounts
    pool = ThreadPoolExecutor(max_workers = None)
    threads = [pool.submit(clear_account, account) for account in account_ids]
    for t in threads:
        try:
            t.result()
        except ClientError as setup_error:
            print(setup_error.response['Error']['Message'])
            continue
