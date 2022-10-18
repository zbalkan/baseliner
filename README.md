# baseliner

Generate a custom profile based on an existing STIG, and utilize STIG ecosystem for further scans.

The CLI prompts for a profile, and expects user to accept or deny each rule. User must provide a rationale when denied a rule.

## Usage

```shell
usage: main.py [-h] -i IN_PATH -o OUT_PATH

Generate Custom STIG profile for baseline.

options:
  -h, --help   show this help message and exit
  -i IN_PATH   Path to STIG XML file
  -o OUT_PATH  Path for modified STIG XML file
```
