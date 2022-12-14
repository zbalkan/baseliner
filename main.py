#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from datetime import datetime as dt

from stigAnsible import StigAnsible
from stigGenerator import StigGenerator
from stigParser import Benchmark, Group, Preference, Profile, StigParser

ENCODING: str = "utf-8"


def main() -> None:

    # Handle arguments
    arg_parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Generate Custom STIG profile baseline of yor choice.")
    if (len(sys.argv)) == 1:
        arg_parser.print_help()
    arg_parser.add_argument("-i", dest="in_path", type=str, required=True,
                            help="Path to STIG Zip file")
    arg_parser.add_argument("-o", dest="out_path", type=str, required=False,
                            help="Directory for modified STIG Zip file (default: input directory)")
    arg_parser.add_argument("-a", dest="ansible_path", type=str, required=False,
                            help="Path to STIG Ansible Zip file")

    args: argparse.Namespace = arg_parser.parse_args()

    stig_file: str = os.path.abspath(args.in_path)
    if (stig_file.endswith(".zip") is False):
        raise Exception("Invalid input parameter.")

    if (args.out_path is None):
        output_dir: str = os.path.dirname(stig_file)  # Default value
    else:
        output_dir = os.path.abspath(args.out_path)
    if (os.path.isdir(output_dir) is False):
        raise Exception("Invalid otput parameter.")

    # Create folder for task
    timestamp: str = dt.now().strftime("%Y%m%d%H%M%S")
    task_dir: str = f"baseliner_{timestamp}"
    os.mkdir(os.path.join(
        output_dir, task_dir))
    output_dir = os.path.join(output_dir, task_dir)

    ansible_zip_file: str = ""
    generate_ansible: bool = False
    if (args.ansible_path):
        generate_ansible = True
        ansible_zip_file = os.path.abspath(args.ansible_path)
        if (ansible_zip_file.endswith(".zip") is False):
            raise Exception("Invalid input parameter.")

    # Start processing
    stig_parser: StigParser = StigParser.parse_zip(zip_file=stig_file)
    benchmark: Benchmark = stig_parser.Benchmark

    selected_profile: Profile = StigGenerator.prompt_profile(
        benchmark=benchmark)
    selected_groups: list[Group] = StigGenerator.filter_groups(
        benchmark=benchmark, selected_profile=selected_profile)

    print(f"{len(selected_groups)} rules selected out of {len(benchmark.Group)} by selecting profile \"{selected_profile.title}\"")

    preferences: list[Preference] = StigGenerator.prompt_preferences(
        selected_groups=selected_groups)

    custom_profile: Profile = StigGenerator.get_custom_profile(
        preferences=preferences)

    StigGenerator.generate(stig_file, output_dir,
                           benchmark, preferences, custom_profile)

    if (generate_ansible):
        script: StigAnsible = StigAnsible()
        script.generate(
            ansible_zip=ansible_zip_file, output_directory=output_dir)

    print("Completed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Cancelled by user.')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as ex:
        print('ERROR: ' + str(ex))
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(1)
