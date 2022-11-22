#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from shutil import which

from stigGenerator import StigGenerator
from stigParser import Benchmark, Group, Preference, Profile, StigParser

ENCODING: str = "utf-8"


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which

    return which(name) is not None


def main() -> None:

    argParser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Generate Custom STIG profile baseline of yor choice. Audit and remediate against your baseline.")
    if (len(sys.argv)) == 1:
        argParser.print_help()
    argParser.add_argument("-i", dest="in_path", type=str, required=True,
                           help="Path to STIG Zip file")
    argParser.add_argument("-o", dest="out_path", type=str, required=False,
                           help="Directory for modified STIG Zip file (default: input directory)")
    argParser.add_argument("-r", action="store_true",
                           help="Generate audit report as HTML (requires OpenScap)")
    argParser.add_argument("-s", action="store_true",
                           help="Generate hardening script as Ansible playbook (requires OpenScap)")

    args: argparse.Namespace = argParser.parse_args()
    input: str = os.path.abspath(args.in_path)
    if (input.endswith(".zip") == False):
        raise Exception("Invalid input parameter.")

    if (args.out_path is None):
        output: str = os.path.dirname(input)  # Default value
    else:
        output = os.path.abspath(args.out_path)
    if (os.path.isdir(output) == False):
        raise Exception("Invalid otput parameter.")

    generateReport: bool = args.r
    generateAnsible: bool = args.s

    # if (generateAnsible or generateReport):
    #     if (which("oscap") is None):
    #         raise Exception("OpenScap is required to use this flag")

    stigParser: StigParser = StigParser.parseZip(input)
    benchmark: Benchmark = stigParser.Benchmark

    selectedProfile: Profile = StigGenerator.prompt_profile(benchmark)
    selectedGroups: list[Group] = StigGenerator.filter_groups(
        benchmark, selectedProfile)

    print(f"{len(selectedGroups)} rules selected out of {len(benchmark.Group)} by selecting profile \"{selectedProfile.title}\"")

    preferences: list[Preference] = StigGenerator.prompt_preferences(
        selectedGroups)

    customProfile: Profile = StigGenerator.get_custom_profile(preferences)
    StigGenerator.generate_profile(customProfile, input, output)
    StigGenerator.generate_rationale(customProfile, preferences, output)

    if (generateReport):
        StigGenerator.generate_report(
            customProfile=customProfile, output=output, benchmarkId=benchmark.id)
    if (generateAnsible):
        StigGenerator.generate_fix(
            customProfile=customProfile, output=output, benchmarkId=benchmark.id)

    StigGenerator.close()

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
