#!/usr/bin/env python3

"""Utility to provision read-only access to all accounts in organization.

Read-only access to all accounts in organization is granted to some trusted
account in the same organization or some external account.

The following operations are implemented:
* setup -- create policy and role for read-only access in every account
* clear -- delete policy and role for read-only access from every account
* check -- check if policy and role for read-only access exist in every account

    Functions:
        parse_args() -> Namespace object
        get_credentials(file) -> dict
        main()
"""

from functions import *
from setup import *
from clear import *
from check import *

import argparse, sys
import logging
import traceback

def parse_args():
    """Parsing command line arguments and parameters.

    Command line parameters and options are checked and added to Namespace
    object which is returned.

        Parameters:
            None

        Returns:
            argp.parse_args(): Namespace object
    """

    def add_optional_args(parser):
        parser.add_argument('-v', '--verbose',
                            help='increase output verbosity',
                            action='store_true')
        parser.add_argument('-f', '--file', nargs=1, default=FWD_SETUP_CSV,
                            help='specify file with admin user credentials')

    argp = argparse.ArgumentParser()
    subp = argp.add_subparsers(dest='cmd', metavar='COMMAND', required=True)

    clear = subp.add_parser('clear',
                            help='remove read-only policies and roles that were created')
    add_optional_args(clear)

    check = subp.add_parser('check',
                            help='check if read-only policies and roles are created')
    add_optional_args(check)

    setup = subp.add_parser('setup', help='setup read-only policies and roles')
    add_optional_args(setup)
    mgroup = setup.add_mutually_exclusive_group(required=True)
    mgroup.add_argument('-a', '--account',
        help='account to set as a trusted one')
    mgroup.add_argument('-e', '--external-id',
        help='External-ID to use with the Forward Networks account as a trusted one')

    return argp.parse_args()

def get_credentials(file):
    """Determining current user credentials from provided CSV file.

    When adding AWS admin user an IAM or adding security key for existing admin
    user download CSV file with user's Access key ID and Secret access key that
    are used as credentials. Return dictionary with this data.

        Parameters:
            file : str
                path to CSV file with admin user's credentials

        Returns:
            credentials : dict
                credentials of admin user
    """

    with open(file, mode='r') as cvsfile:
        reader = csv.reader(cvsfile)
        i = 0
        keys = []
        values = []
        user_data = {}
        for row in reader:
            i = i + 1
            if i == 1:
                keys = row
                continue
            else:
                values = row
                break

        user_data = {
            keys[i]: values[i] for i in range(len(keys))
        }

    credentials = {
        'AccessKeyId': user_data['Access key ID'],
        'SecretAccessKey': user_data['Secret access key'],
        'SessionToken': ""
    }

    return credentials

def main():
    """Main function that implements all functionality.

    Command line parameters are checked and appropriate operations are
    performed. If command line parameters are invalid or mutually exclusive
    then script usage guidance is displayed.

        Parameters:
            None

        Returns:
            None
    """

    args = parse_args()

    # determine location of csv file with credentials
    if type(args.file) is list:
        fwd_setup_file = args.file[0]
    else:
        fwd_setup_file = args.file

    logging.basicConfig(
        level = logging.DEBUG if args.verbose else logging.WARN,
        format = f'%(asctime)s %(levelname)s %(message)s'
    )

    try:
        # get credentials from file
        credentials = get_credentials(fwd_setup_file)

        # determine management account
        mgmt_account = get_current_account(credentials)

        if args.cmd == 'check':
            check(credentials, mgmt_account)
        elif args.cmd == 'clear':
            clear(credentials, mgmt_account)
        elif args.cmd == 'setup':
            if args.account != None:
                trusted_account = args.account
            elif args.external_id != None:
                trusted_account = FWD_ACCOUNT_ID
            else:
                trusted_account = mgmt_account
            setup(trusted_account, args.external_id, credentials, mgmt_account)
    except BaseException as e:
        if args.verbose:
            traceback.print_exc()
        else:
            print(e)
        sys.exit(2)

if __name__ == '__main__':
    main()
