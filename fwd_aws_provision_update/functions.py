"""Functions used in operations with read-only IAM roles and policies.

    Functions:
        get_current_account(credentials) -> str
        list_accounts(credentials) -> list
        switch_roles(account, credentials) -> dict
        check_managed_policy(policy_name, credentials) -> bool
        check_role(role_name, credentials) -> bool
        create_policy(policy_name, document, credentials) -> dict
        create_role(role_name, document, policy_name, credentials)
        delete_policy(policy_name, credentials)
        delete_role(role_name, policy_name, credentials)
        aws_service_client(service, credentials) -> class
        usage()
"""

from definitions import *
import boto3
import sys
import csv
from botocore.config import Config

def get_current_account(credentials):
    """Get ID of account that is accessed using provided credentials.

        Parameters:
            credentials : dict
                AWS user credentials

        Returns:
            account : str
                ID of account that AWS user belongs to
    """

    sts_client = aws_service_client('sts', credentials)

    account = sts_client.get_caller_identity()['Account']

    return account

def list_accounts(credentials):
    """List all accounts in organization.

    It is supposed that the script is run with credentials of admin user in
    management account. Therefore the user is able to list all accounts in the
    organization. If the user does not have sufficient permissions then the
    summary of thrown exception is sent to stdout.

        Parameters:
            credentials : dict
                credentials of AWS user who runs the script

        Returns:
            account_id_list : list
                list of dictionaries each of which contains ID and name of
                some particular account in organization
    """

    organizations_client = aws_service_client('organizations', credentials)

    response = organizations_client.list_accounts()

    accounts = response['Accounts']

    all_accounts_records = []
    for account in accounts:
        account_record = {}
        account_record['id'] = account['Id']
        account_record['name'] = account['Name']
        all_accounts_records.append(account_record)

    return all_accounts_records

def switch_roles(account, credentials):
    """Get credentials for switching role into account.

    Every account created in organization has by default IAM role
    OrganizationAccountAccessRole that allows admin access from management
    account. Switching roles is based on obtaining temporary credentials
    from STS service.

        Parameters:
            account : str
                ID of account to switch into
            credentials : dict
                credentials of AWS user who runs the script

        Returns:
            assumed_role_credentials : dict
                credentials to be used to access account
    """

    sts_client = aws_service_client('sts', credentials)

    assumed_role_object = sts_client.assume_role(
        RoleArn="arn:aws:iam::"+account+":role/OrganizationAccountAccessRole",
        RoleSessionName="AssumeRole-"+account
    )

    assumed_role_credentials = assumed_role_object['Credentials']
    return assumed_role_credentials

def check_managed_policy(policy_name, credentials):
    """Check if the customer managed IAM policy exists in account.

        Parameters:
            policy_name : str
                name of customer managed IAM policy existence of which is
                checked
            credentials : dict
                credentials to be used to access account

        Returns:
            search_result : bool
                True if the policy was found, False otherwise
    """

    iam_client = aws_service_client('iam', credentials)

    response = iam_client.list_policies(
        Scope = 'Local',
        PathPrefix = '/'
    )

    search_result = False
    for policy in response['Policies']:
        if policy['PolicyName'] == policy_name:
            search_result = True
    return search_result

def check_role(role_name, credentials):
    """Check if the IAM role exists in account.

        Parameters:
            role_name : str
                name of IAM role existence of which is checked
            credentials : dict
                credentials to be used to access account

        Returns:
            search_result : bool
                True if the role was found, False otherwise
    """

    iam_client = aws_service_client('iam', credentials)

    response = iam_client.list_roles()

    search_result = False
    for role in response['Roles']:
        if role['RoleName'] == role_name:
            search_result = True
    return search_result

def create_policy(policy_name, document, credentials):
    """Create IAM policy in account.

        Parameters:
            policy_name : str
                name of IAM policy to be created in account
            document : str
                JSON document that defines content for the new policy
            credentials : dict
                credentials to be used to access account

        Returns:
            response : dict
                content of the policy that was created
    """

    iam_client = aws_service_client('iam', credentials)

    response = iam_client.create_policy(
        PolicyName = policy_name,
        Path = '/',
        PolicyDocument = document
    )

    return response

def create_role(role_name, document, policy_name, credentials):
    """Create IAM role in account.

        Parameters:
            role_name : str
                name of IAM role to be created in account
            document : str
                JSON document that defines content for the new role
            credentials : dict
                credentials to be used to access account

        Returns:
            None
    """

    iam_client = aws_service_client('iam', credentials)

    iam_client.create_role(
        RoleName = role_name,
        Path = '/',
        AssumeRolePolicyDocument = document
    )

    account = get_current_account(credentials)

    policy_arn = "arn:aws:iam::" + account + ":policy/" + policy_name
    iam_client.attach_role_policy(
        RoleName = role_name,
        PolicyArn = policy_arn
    )

def delete_policy(policy_name, credentials):
    """Delete IAM policy in account.

        Parameters:
            policy_name : str
                name of IAM policy to be deleted in account
            credentials : dict
                credentials to be used to access account

        Returns:
            None
    """

    account = get_current_account(credentials)

    policy_arn = "arn:aws:iam::" + account + ":policy/" + policy_name
    iam_client = aws_service_client('iam', credentials)

    iam_client.delete_policy(
        PolicyArn = policy_arn
    )

def delete_role(role_name, policy_name, credentials):
    """Delete IAM role in account.

        Parameters:
            role_name : str
                name of IAM role to be deleted in account
            policy_name : str
                name of IAM policy attached to role that is to be deleted
            credentials : dict
                credentials to be used to access account

        Returns:
            None
    """

    account = get_current_account(credentials)

    policy_arn = "arn:aws:iam::" + account + ":policy/" + policy_name
    iam_client = aws_service_client('iam', credentials)

    iam_client.detach_role_policy(
        RoleName = role_name,
        PolicyArn = policy_arn
    )

    iam_client.delete_role(
        RoleName = role_name
    )

def aws_service_client(service, credentials):
    """Create client to access AWS service.

        Parameters:
            service : str
                name of service for which the client is created
            credentials : dict
                credentials to be used to access the service

        Returns:
            service_client : class 'botocore.client.<service>'
                class used to access AWS service
    """

    config = Config(
        retries = {
            'max_attempts': sys.maxsize - 1000,
            'mode': 'standard'
        }
    )

    service_client = boto3.client(
        service,
        aws_access_key_id = credentials['AccessKeyId'],
        aws_secret_access_key = credentials['SecretAccessKey'],
        aws_session_token = credentials['SessionToken'],
        config = config
    )

    return service_client
