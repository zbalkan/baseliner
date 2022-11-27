# baseliner

Generate a custom profile based on an existing STIG, and utilize STIG ecosystem for further scans.

The CLI prompts for a profile, and expects user to accept or deny each rule. User must provide a rationale when denied a rule.

The application accepts a valid STIG zip file as an input. It will export a modified STIG Zip file with new profile included, and an XML file for rationale for the omitted requirements.

When provided, the `-a` argument accepts a STIG Anzible zip file downloaded from DoD Library. The script parses the tasks in Ansible, excludes the rules omitted by the user, and exports a new main file. Copy the generated `custom.tasks.main.yml` file under `roles/<STIG name>/tasks/` folder bu overwriting the current main.yml file.

## Usage

```shell
usage: main.py [-h] -i IN_PATH [-o OUT_PATH] [-a ANSIBLE_PATH]

Generate Custom STIG profile baseline of yor choice.

options:
  -h, --help       show this help message and exit
  -i IN_PATH       Path to STIG Zip file
  -o OUT_PATH      Directory for modified STIG Zip file (default: input directory)
  -a ANSIBLE_PATH  Path to STIG Ansible Zip file
```

## Installation and development

- Clone the repository
- Run `pip install -r requirements.txt`
