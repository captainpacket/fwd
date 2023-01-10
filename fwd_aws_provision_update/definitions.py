"""Definitions of objects used in operations with read-only roles and policies.

    Variables:
        FWD_ACCOUNT_ID : str
            ID of Forward Networks AWS account that is trusted with read-only
        APPHOST : str
            IP/DNS name of Forward Enterprise instance
        NETWORKID : str
            ID of Forward Enterprise instance to POST updates
        SETUPID : str
            ID of Forward Enterprise AWS setup name
        FWD_SETUP_CSV: str
            default CSV file name in the current folder that contains admin
            user credentials
        REGIONS : str
            Filename of AWS regions to collect from
        APPCREDS : str
            Filename of Forward Enterprise API credentials
        FWD_READ_ONLY_POLICY_NAME : str
            name of read-only IAM policy that is created in all accounts of
            organization
        FWD_READ_ONLY_POLICY_DOCUMENT : str
            JSON description of read-only IAM policy that is created in all
            accounts of organization
        FWD_READ_ONLY_ROLE_NAME : str
            name of read-only IAM role that is created in all accounts of
            organization
        FWD_ASSUME_ROLE_POLICY_DOCUMENT : str
            JSON description of read-only IAM role that is created in all
            accounts of organization in case when trusted account belongs to
            organization
        FWD_ASSUME_ROLE_POLICY_DOCUMENT_EXTERNAL_ID : str
            JSON description of read-only IAM role that is created in all
            accounts of organization in case when Forward Networks account is
            used as a trusted one
        OUTPUT_FILENAME : str
            file name to which the list of read-only IAM roles is written
"""

FWD_ACCOUNT_ID = '453418124061'

APPHOST = "fwd.app"

NETWORKID = "154820"

SETUPID = "aws_collect"

FWD_SETUP_CSV = "fwd_setup.csv"

REGIONS = "regions.txt"

APPCREDS = "creds.txt"

FWD_READ_ONLY_POLICY_NAME = 'Forward_Enterprise'
FWD_READ_ONLY_POLICY_DOCUMENT = \
    '{ "Version": "2012-10-17", ' \
    '"Statement": [{ "Effect": "Allow", ' \
    '"Action": [ "autoscaling:Describe*", "cloudwatch:ListMetrics", ' \
    '"cloudwatch:GetMetricStatistics", "cloudwatch:Describe*", ' \
    '"directconnect:Describe*", "ec2:Describe*", "ec2:Get*", "ec2:Search*", ' \
    '"globalaccelerator:List*", "workspaces:Describe*", ' \
    '"elasticloadbalancing:Describe*", "network-firewall:Describe*", ' \
    '"network-firewall:List*", "organizations:ListAccounts"], ' \
    '"Resource": "*"}]}'

FWD_READ_ONLY_ROLE_NAME = 'ForwardReadOnlyAccess'
FWD_ASSUME_ROLE_POLICY_DOCUMENT = \
    '{ "Version": "2012-10-17", ' \
    '"Statement": [{ "Effect": "Allow", ' \
    '"Principal": { "AWS": "arn:aws:iam::###TRUSTED ACCOUNT ID###:root"}, ' \
    '"Action": "sts:AssumeRole", "Condition": {}}]}'
FWD_ASSUME_ROLE_POLICY_DOCUMENT_EXTERNAL_ID = \
    '{ "Version": "2012-10-17", ' \
    '"Statement": [{ "Effect": "Allow", ' \
    '"Principal": { "AWS": "arn:aws:iam::' + FWD_ACCOUNT_ID + ':root"}, ' \
    '"Action": "sts:AssumeRole", ' \
    '"Condition": {"StringEquals": {"sts:ExternalId": "###EXTERNAL ID###"}}}]}'

OUTPUT_FILENAME = 'fwd_accounts_data.json'