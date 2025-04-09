## Adding Applications to AON Programatically via NSX Sec tags 
- Using either CLI or non CLI script to dynamically add an application into Aria Ops 4 Networks.
- By doing this via NSX Security tags, membership is dynamic, and the app boundary can be further used in analysis or metrics etc 

<img src="https://github.com/defaultroute0/vrni/blob/master/images/app_disc.gif" alt="Sample Image" width="4000">
Click on image to enlarge

## Using AON to check for precence of NSX DFW Rule based on IP addresses
Usage
````

````
https://github.com/defaultroute0/vrni/blob/09678d8bef73621ab7f3de4f250248574490c4dc/pythonexamples/create-app-apptier-cli.py


Usage
Command-line Arguments
query (Required): A string query specifying the firewall rules you want to search for. For example, you can search for firewall rules with a specific source IP.
````
  python CheckForRuleCLI.py "firewall rules where source ip = 1.2.3.4" will automatically append this  "Source != any and Destination != any"
````
--exclude-source-any (Optional): If provided, the script will exclude rules where the source is any.

--exclude-destination-any (Optional): If provided, the script will exclude rules where the destination is any.
