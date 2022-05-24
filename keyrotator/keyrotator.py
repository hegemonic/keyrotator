# -*- coding: utf-8 -*-
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""keyrotator: Key management utility for Google Cloud service account keys."""

import argparse
import logging
import sys
import time

from cleanup import CleanupCommand
from create import CreateCommand
from delete import DeleteCommand
from list import ListCommand
from version import __version__


def _init_arg_parser():
  IAM_ACCOUNT_DESCRIPTION = "The IAM service account ID."
  PROJECT_ID_DESCRIPTION = "The project ID of the key."
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers()

  parser.add_argument("--version", action="version", version=__version__)

  parser_cleanup = subparsers.add_parser("cleanup")
  parser_cleanup.add_argument(
      "--project-id", help=PROJECT_ID_DESCRIPTION, required=True)
  parser_cleanup.add_argument(
      "--iam-account", help=IAM_ACCOUNT_DESCRIPTION, required=True)
  parser_cleanup.add_argument(
      "--key-max-age", help="The maximum age of a key, in days, to exclude "
      "from deletion. Older keys are deleted.", required=True, type=int)
  parser_cleanup.set_defaults(func=Cleanup)

  parser_create = subparsers.add_parser("create")
  parser_create.add_argument(
      "--project-id", help=PROJECT_ID_DESCRIPTION, required=True)
  parser_create.add_argument(
      "--iam-account", help=IAM_ACCOUNT_DESCRIPTION, required=True)
  # TODO(jefesaurus): add choices
  parser_create.add_argument(
      "--key-type", help="The type of private key to create.")
  # TODO(jefesaurus): add choices
  parser_create.add_argument(
      "--key-algorithm", help="The algorithm of the key to create.")
  parser_create.add_argument(
      "--output-file", help="The file name of the newly created key.")
  parser_create.set_defaults(func=Create)

  parser_delete = subparsers.add_parser("delete")
  parser_delete.add_argument(
      "--project-id", help=PROJECT_ID_DESCRIPTION, required=True)
  parser_delete.add_argument(
      "--iam-account", help=IAM_ACCOUNT_DESCRIPTION, required=True)
  parser_delete.add_argument(
      "--key-id", help="The ID of the key to delete.", required=True)
  parser_delete.set_defaults(func=Delete)

  parser_list = subparsers.add_parser("list")
  parser_list.add_argument(
      "--project-id", help=PROJECT_ID_DESCRIPTION, required=True)
  parser_list.add_argument(
      "--iam-account", help=IAM_ACCOUNT_DESCRIPTION, required=True)
  parser_list.set_defaults(func=List)

  return parser


def main():
  log_filename = "keyrotator" + time.strftime("-%Y-%m-%d-%H%M") + ".log"
  logging.basicConfig(filename=log_filename, level=logging.INFO)
  logging.getLogger("").addHandler(logging.StreamHandler())
  logging.info("Logging established in %s.", log_filename)

  arg_parser = _init_arg_parser()
  args = arg_parser.parse_args()
  args.func(args)


def Cleanup(args):
  """For the specified project, account, and key age, delete invalid keys.

  1) List keys for the given GCP Project ID and Service Account.
  2) Determine Key IDs that meet the key_max_age requirement.
  3) Perform a delete for the matching Key IDs.

  Args:
    args: The parsed arguments from the command line.
  """
  command = CleanupCommand()
  sys.exit(command.run(args.project_id, args.iam_account, args.key_max_age))


def Create(args):
  """Creates a new key for an account with the specified key type and algorithm.

  If no key type or key algorithm is provided, it will default the key type to
  TYPE_GOOGLE_CREDENTIALS_FILE format and the key algorithm to KEY_ALG_RSA_4096.
  The resulting key will be output to stdout by default.

  Args:
    args: The parsed arguments from the command line.
  """
  command = CreateCommand()
  sys.exit(command.run(args.project_id, args.iam_account, args.key_type,
                       args.key_algorithm, args.output_file))


def Delete(args):
  """Deletes a specific key for an account.

  Args:
    args: The parsed arguments from the command line.
  """
  command = DeleteCommand()
  sys.exit(command.run(args.project_id, args.iam_account, args.key_id))


def List(args):
  """List keys for service account.

  Args:
    args: The parsed arguments from the command line.
  """
  command = ListCommand()
  sys.exit(command.run(args.project_id, args.iam_account))


if __name__ == "__main__":
  main()
