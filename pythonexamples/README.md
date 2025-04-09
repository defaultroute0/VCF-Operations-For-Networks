## Adding Applications to AON Programatically via NSX Sec tags 
- Using either CLI or non CLI script to dynamically add an application into Aria Ops 4 Networks.
- By doing this via NSX Security tags, membership is dynamic, and the app boundary can be further used in analysis or metrics etc 

<img src="https://github.com/defaultroute0/vrni/blob/master/images/app_disc.gif" alt="Sample Image" width="4000">
Click on image to enlarge

## Using AON to check for precence of NSX DFW Rule based on IP addresses
Usage
````
  python CheckForRuleCLI.py "firewall rules where source ip = 1.2.3.4 and Source != any and Destination != any"
````
