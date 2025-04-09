# Example 1 - Adding Applications to AON Programatically via NSX Sec tags 
- Using either CLI or non CLI script to dynamically add an application into Aria Ops 4 Networks.
- By doing this via NSX Security tags, membership is dynamic, and the app boundary can be further used in analysis or metrics etc 

<img src="https://github.com/defaultroute0/vrni/blob/master/images/app_disc.gif" alt="Sample Image" width="4000">
Click on image to enlarge

# Example 2 - Using AON to check for precence of NSX DFW Rule based on IP addresses

## Files
- `create-app-apptier-cli.py`
- `create-app-apptier.py`

## Firewall Rules Query Script

This script allows you to query firewall rules using the `Aria Operations` API and retrieve the details of the matching rules based on various parameters such as source IP, and exclusion filters for the `Source` and `Destination` fields. It provides flexibility to filter out any rules with `Source = any` and `Destination = any` using command-line flags.

### Files
- `CheckForRule.py`
- `CheckForRuleCLI.py`

### Usage

#### Command-line Arguments

#### Options:

- `--exclude-src-any`: Exclude `any` from the **Source** field.
- `--exclude-dest-any`: Exclude `any` from the **Destination** field.
- `--exclude-both-any`: Exclude `any` from both **Source** and **Destination** fields.
  
If no exclusion options are used, the script will show all rules which match the logic, including rules using 'any' in source/destination

#### Example:

- **Exclude `any` from the Source field only**:

  ```bash
  python CheckForRuleCLI.py "firewall rules where source ip = 1.2.3.4" --exclude-src-any

<img src="https://github.com/defaultroute0/vrni/blob/master/images/app_disc.gif" alt="Sample Image" width="4000">
Click on image to enlarge
