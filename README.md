# baseliner

Generate a custom profile based on an existing STIG, and utilize STIG ecosystem for further scans.

The CLI prompts for a profile, and expects user to accept or deny each rule. User must provide a rationale when denied a rule.

The application accepts a valid STIG zip file as an input. It will export a modified STIG Zip file with new profile included, and an XML file for rationale for the omitted requirements.

## Prerequisites 

- Python 3.7+
- pip
- OpenScap

## Usage

```shell
usage: main.py [-h] -i IN_PATH [-o OUT_PATH] [-r] [-s]

Generate Custom STIG profile baseline of yor choice. Audit and remediate against your baseline.

options:
  -h, --help   show this help message and exit
  -i IN_PATH   Path to STIG Zip file
  -o OUT_PATH  Directory for modified STIG Zip file (default: input directory)
  -r           Generate audit report as HTML (requires OpenScap)
  -s           Generate hardening script as Ansible playbook (requires OpenScap)
```

## Installation and development

- Clone the repository
- Run `pip install -r requirements.txt`
