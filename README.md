# VMware Aria Operations for Networks
 (formerly vRealize Network Insight) - Useful Queries

1. [Trial Process](#overview)
	1. [Prerequisites](#prerequisites)
	2. [Installation](#installation)
	3. [Archiving flows to vRLI](#vRLI)
	4. [Import recommended fw rules to NSX-T/VMC on AWS](#ImportFW)
2. [General Queries](#general)
	1. [Searches/Demos](#search)
	2. [TopN](#topn)
	3. [Workloads VMs](#query-vm2)
	5. [Applications](#apps)
	6. [Network Stuff](#network)
	7. [Path Tracing](#tracing)
	8. [Flows](#flows)
	9. [Dubious Flows](#badflows)
	10. [Physical Flows](#phyflows)
	11. [Security Stuff](#security)
	12. [Lateral Threat, Internal Traffic](#lateral)
	13. [Change and Auditing](#audit)
	14. [Managing NSX Domain](#nsxday2)
	15. [VMC](#vmc)
	16. [Public Cloud](#publiccloud)
	17. [VeloCloud](#velocloud)
	18. [Kubernetes](#k8s)
3. [Traffic Analysis Queries](#queries)
	1. [Security](#query-security)
	2. [VM by Application](#query-vm-application)
	3. [VM by Network](#query-vm-network)
	4. [Traffic Analysis - L2 Network](#query-traffic-network)
	5. [Traffic Analysis - Routing and Aggregation](#query-traffic-routing)
	6. [Traffic Analysis - Ports and Services](#query-traffic-services)
	7. [VMs, Routed via Specific L3 Device](#query-vms-routed-specific)
	8. [VMs, Hairpinning and L3 Subnet Dependencies](#query-vms-hairpinning)
	9. [Flows, Aggegration Prefix - Traffic Stats](#query-flows-aggregation)
	10. [Flows, VM-VM, Routed, on Same Host](#query-flows-routed-samehost)
	11. [Flows, VM-VM, Routed, via any L3 Router](#query-flows-routed-any)
	12. [Flows, VM-VM, Routed, via specific L3 Router](#query-flows-routed-specific)
	13. [Moving, Migrating Applications](#migration)
	14. [Virtual Network Assessment](#vna)
3. [Using vRNI via API](#api)
4. [Import/Export Applications](#applications)

## vRNI Trial Process <a name="overview"></a>

The first step is to register for the VRNI trial and download the appliance files.  
You can then copy the OVAs onto a vSphere Datastore in your management environment ready to go, as this will greatly simplify the process.  

Also - please read the pre-requisites below as they relate to product versions, vCenter permissions, and the Distributed Switch.  

To get access to the 60-day vRNI Trial OVA's and Trial Key you can go here:
http://vmware.com/go/vna-field/

To download the appliances (and get the license key), you can sign in using your my.vmware.com credentials.
If you do not have a my.vmware.com account - select "create an account" to register first.

You will then get access to download the latest vRNI OVAs:
- VMware-vRealize-Network-Insight-X.X.X.XXXXXXXXXX-platform.ova
- VMware-vRealize-Network-Insight-X.X.X.XXXXXXXXXX-proxy.ova

Main documentation page:  
https://docs.vmware.com/en/VMware-vRealize-Network-Insight/index.html

### vRNI Prerequisites <a name="prerequisites"></a>
For the vRNI trial, there are 2x OVA images (mentioned above) to be imported into a vSphere environment.  
These will be configured to begin collecting vCenter inventory and VDS flow information from the virtual environment.  

Please take a look at the pre-requisites below.

To set up these VMs - you will require:
1. 2x static IP addresses to be allocated from a MGMT environment (1 IP per VM)
2. VMs to be imported into a MGMT environment (OVAs to be copied over to vCenter datastore first, but not yet deployed)
3. These IP addresses require connectivity/access (L2 or L3) to the MGMT network of vCenter and ESX host mgmt VMK ports.
	
	```
	ESXi Hosts -> Collector VM (UDP 2055).
	Collector VM  -> vCentre (TCP 443).
	Collector VM -> Platform VM (TCP 443).
	https://ports.vmware.com/home/vRealize-Network-Insight
	```
	
4. Environment must be using the Distributed Virtual Switch
5. vCenter Server credentials with privileges:
- Distributed Switch: Modify
- dvPort group: Modify

More details on permissions here:  
https://docs.vmware.com/en/VMware-vRealize-Network-Insight/6.4/com.vmware.vrni.install.doc/GUID-F4F34425-C40D-457A-BA65-BDA12B3ABE45.html

6. Once installed - the vRNI Platform will modify and enable IPFIX flows on the VDS
- This will be a change (although non-impacting) - please ensure any change control items are covered  
- Verify current ESX VDS IPFIX configuration before proceeding

From here we can:
- Create some high level VM 'Application' grouping constructs
- Typically gather data for 3-5 days (or more) and generate reports for app dependencies, routed, switched etc..
- Plan logical constructs for a transition to NSX

Here are the vRNI VM requirements (refer to Install documentation below):

vRealize Network Insight **Platform** OVA (XL):  
- 18 cores - Reservation 100%
- 64 GB RAM - Reservation - 100%
- 2 TB - HDD, Thin provisioned

** N.B: To use 'Flow based Application Discovery' OR  'Network Intents and Assurance'- use XL Brick size for the platform (18 core / 64GB RAM / 2TB disk)
Basically if you are evaluating how machine learning can disovery applications, its a must to check this out.
https://youtu.be/bqZSBwv55vk

vRealize Network Insight **Collector** OVA (XL):  
- 9 cores - Reservation 100%
- 24 GB RAM - Reservation - 100%
- 200 GB - HDD, Thin provisioned

VMware vCenter Server (version 5.5+ and 6.0+):
- To configure and use IPFIX

VMware ESXi:
- 5.5 Update 2 (Build 2068190) and above
- 6.0 Update 1b (Build 3380124) and above

Full list of supported data sources:  
https://docs.vmware.com/en/VMware-vRealize-Network-Insight/6.4/com.vmware.vrni.using.doc/GUID-4BA21C7A-18FD-4411-BFAC-CADEF0050D76.html#GUID-4BA21C7A-18FD-4411-BFAC-CADEF0050D76

VMware Tools ideally installed on all the virtual machines in the data center.  
This helps in identifying the VM to VM traffic.  

### Installation Steps <a name="installation"></a>

I would usually block out a morning or afternoon (around 2 hours) to complete this.  
If you have already copied the VMs to vCenter this can be < 1 hour.

vRealize Network Insight Install Documentation:  
https://www.vmware.com/support/pubs/vrealize-network-insight-pubs.html

This covers the install process - fairly straight forward. 
https://docs.vmware.com/en/VMware-vRealize-Network-Insight/6.4/com.vmware.vrni.install.doc/GUID-F4F34425-C40D-457A-BA65-BDA12B3ABE45.html

High-level steps:
https://docs.vmware.com/en/VMware-vRealize-Network-Insight/6.4/com.vmware.vrni.install.doc/GUID-EA58F67F-B794-403E-BE54-16A4C2CA309C.html
1. Import Platform VM OVA and power up
2. Connect HTTPS to Platform VM and run through wizard using admin@local as login and your password you set
3. Enter License Key - this is for the 60-day trial
4. Generate shared key from Platform VM
5. Import Proxy VM and enter shared key
6. Finalise Proxy install via setup CLI
7. Login to Platform VM UI (HTTPS) admin@local and configure vCenter / VDS datasources (IPFIX)

## Archiving flows to vRLI <a name="vRLI"></a>
Archiving flows to vRLI
https://github.com/PowervRNI/powervrni/tree/master/examples/archive-flows-to-vrli

## Import recommended fw rules to NSX-T/VMC on AWS <a name="ImportFW"></a>
Import recommended fw rules to NSX-T/VMC on AWS
https://github.com/vrealize-network-insight/vrni-rule-import-vmc-nsxt


## General Queries <a name="general"></a>

vRNI is a big data analytics set of of end to end environment, physical, virtual, AWS, NSX-T, Nexus Switches, ASA Palo firewalls as an example. It's the context of all this against real metrics / network flows which provides great insight to networks, security, operations, and cloud teams. 

The usefulness of these outputs is only as good as the questions asked of the system, as constructed via **queries**  
Here is a useful list

#### Search Posters and Demos <a name="search"></a>
https://vrealize.vmware.com/t/vrealize-network-insight/
https://docs.vmware.com/en/VMware-vRealize-Network-Insight/6.0/com.vmware.vrni.using.doc/GUID-176F5A09-2325-41EA-A315-58738CB4F117.html
https://www.vmware.com/content/dam/digitalmarketing/vmware/en/pdf/datasheet/products/vmw-vrni-search-poster.pdf

Really nice search database:
https://vrealize.vmware.com/sample-exchange/vrealize-network-insight-search-exchange/categories

#### Top List of Entities  <a name="topn"></a>
```
topn
```

#### VMs <a name="query-vm2"></a>
```
vms group by Application
vm group by network address
vm group by subnet
vm by vlan
vm by Max Network Rate 
vm by max network rate where vxlan = '3TierApp02-DB' 
flow where vm in (vm where cpu usage rate > 90%)
vm where CPU Ready Rate > 0.5
vm where CPU Ready Rate  order by Max Network Rate 
vm where cpu usage rate > 80%
vm where CPU Wait Rate order by Max Network Rate 
vm by Read Latency where RW IOPS 
vm by RW IOPS where Max Network Rate and CPU Ready Rate and CPU Wait Rate and Read Latency and RW Throughput and Read IOPS and Read Throughput and Write IOPS and Write Latency and Write Throughput 
vm where Operating System like 'Microsoft Windows Server 2003' or Operating System like 'Microsoft Windows Server 2008' or Operating System like 'Red Hat Enterprise Linux 6' or Operating System like 'Red Hat Enterprise Linux 5' or Operating System like 'SUSE Linux Enterprise 10' group by vlan, Operating System
```

#### Applications you define or learn via ML <a name="apps"></a>
```
application
application 'HIVE Training'
sum(Bytes), sum(Bytes Rate), sum(Retransmitted Packet Ratio), max(Average Tcp RTT) of flows where Destination Application like 'Funbike' 
```

#### Network Stuff <a name="network"></a>
```
l2 network order by VM Count 
L2 Network where VM Count > 0 group by Network Address, VM Count
sum(VM Count) of l2 network order by VM Count
top 10 vlan group by Vlan id, vm count order by sum(Total Network Traffic) in last 7 days
show vlan by Host Count 
10.100.23.43
Vlan 'vlan-10'
Vxlan '3TierApp02-Web'
show vlan by Network Rate 
source L2 Network of Flow order by Session Count 
aci fabric 'NSX-ACI-Fabric1'
port where Max Packet Drops 
aci fabric
```

- Routers
```
Show router interface
port where Max Packet Drops 
router interface where Rx Packet Drops > 0
router interface order by Max Network Rate  
router where OSPF  
show Router Interface Packet Drop
port where Max Packet Drops 
show Router Interface where Interface Utilization > 70
show vrf
show router
show Route '10.114.219.232/29'  
show route where change
vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))
vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1')) group by VLAN
```

- Switches
```
show Juniper Switch Data Source 
show Switch Port where Carrier Losses Detected 
show Switch Port where Collisions Detected 
show Switch Port where change
show Switch Port where event
show Switch Port where problem
switch where Switch Ports like 'Ethernet1/1' 
show Switch Port where interface utilization
show Switch Port where  Interface Peak Buffer Utilization  
show Switch Port where Learnt Mac Address = '00:25:90:EB:BA:EE' 
show Switch Port where Learnt IP Address like '10.114.219.139' 
show Switch Port where Network Rcv Errors 
port where Max Packet Drops 
show Switch Port where Jumbo Rx Packets 
show Switch Port where Administrative Status like 'UP' and Operational Status like 'DOWN'  
show Switch Port where Discarded Tx Packets 
show Switch Port where Network Out Qlen != 0
```

#### Path Tracing <a name="tracing"></a>
```
VMware VM 'Web03-ACI' to VMware VM 'DB01a-ACI'
```

#### Flows <a name="flows"></a>
```
flows    // then >> flow insights in topright 
flows  in last 72 hours
flow where vm in (vm where cpu usage rate > 90%)
show flows where Subnet Network like '10.173.164.0/24' and Destination Continent != 'North America' 
flows where Destination Port == 3389
list(destination VM) of flow where destination port = 53  //listening on inbound UDP53/TCP53
show flows between Application 'tanzu tees'  and Application 'HIVE Training'
show flows from Cluster 'Cluster-1' to Cluster 'PKS' 
sum(bytes) of flows group by subnet order by sum(bytes)
sum(bytes) of flow group by port.ianaPortDisplay  //change timerange
sum(bytes) of flow where Flow Type = 'Switched' group by Network Address order by avg(Bytes Rate)
sum(bytes) of flows where Flow Type = 'Switched' group by source vm, destination vm order by avg(Bytes Rate)
sum(bytes) of flow where Flow Type = 'Routed' group by Source Subnet Network, Destination Subnet Network order by avg(Bytes Rate)
sum(bytes) of flows where Flow Type = 'Routed' group by source vm, destination vm order by avg(Bytes Rate)
sum(bytes) of flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))) AND (Flow Type = 'Routed' and Flow Type = 'Internet')
hairpinning: sum(Bytes) of flows where (Flow Type = 'Routed' and Flow Type = 'Same Host') group by Source VM, Destination VM order by avg(Byte Rate)
hairpinning: sum(bytes), avg(Bytes Rate) of flows where (Flow Type = 'Routed' and Flow Type = 'Same Host')
```

- Over a time series
```
series(sum(bytes rate)) of Flows where Application = '3TierApp02' 
series(sum(byte rate),300) of flow where destination application  = 'Funbike' and Flow Type = 'East-West' 
```

#### Dubious Flows <a name="badflows"></a>
```
vm where Incoming Port = 445 and Operating System like 'Microsoft Windows 10 (64-bit)' 
vm where Operating System like 'Microsoft Windows XP Professional (32-bit)' 
flow where Destination Country like 'Russia' 
flows where Destination Port == 3389 and Source Country == 'China'
flows where Destination Port == 3389 group by Destination VM, Source Country
flow where destination port = 22 and source continent not 'oceania' order by bytes rate 
show flows from Cluster 'Management' to 'Internet-Gateway' 
Incomplete TCP Session desc
```

#### Physical Flows <a name="phyflows"></a>
```
show flow where flow type = 'Source is Physical' group by port.ianaPortDisplay
flow where Flow Type = 'Source is Physical' or Flow Type = 'Destination is Physical' group by  VM 
flow where Flow Type = 'Source is Physical' or Flow Type = 'Destination is Physical' group by  L2 Network
flow where Flow Type = 'Source is Physical' or Flow Type = 'Destination is Physical' group by  Application
```


#### Security Rules <a name="security"></a>
```
plan security
NSX-T Manager 'SC2nsxt-01.cmbu.local' 
pci dashboard
pci compliance of Cluster 'Cluster-1'
Firewall Rules
Security Tag 'ST-Tito-Web' 
show  'Unused NSX Firewall Rules' 
show 'Unused DFW Rules' 
show  Firewall Rule Masked Alert 
firewall rules where Service Any = true
firewall rules where Service Any = true and action = ALLOW and destination ip = '0.0.0.0'
Ipset where Indirect Incoming Rules is not set and Indirect Outgoing Rules is not set and Direct Incoming Rules is not set and Direct Outgoing Rules is not set
	// Unused IP Sets
firewall rules from VM 'App01-ACI' to VM 'DB02-ACI'
show flow where firewall action = 'DENY' 
firewall rule where flows is not set in last 30 days
firewall rules where Indirect Destination security group 
NSX-T Security Group 'NSX-INTELLIGENCE-GROUP'
top 10 nsx-t firewall rule order by Hit Count
top 10 firewall rules order by Session Count
flows where firewall rule is not set
NSX-T Firewall Rule where  Applied To is not set 
firewall rule where action = allow and service any = true 
flows where firewall rule = 'Allow HTTP for Imagic' 
nsx-t firewall rule where Flow Packets = 0 in last 30 days
new nsx-t firewall rule in last 30 days
VMs group by Firewall Rule
flow  where  IP Address =  70.70.70.31 
flow where  Source IP Address = 70.70.70.31 group by  Security Groups 
flow where  Source IP Address = 70.70.70.31 group by   firewall rule 
NSX-T Security Group 'ryan-hack-servers'
  //  SHows overview, indirect groups, rule counts, flows, direct rules, indirect rules, allowed/denied flows 
NSX-T Firewall Rule 'r1'
    // shows flows, allowed flows, denied flows, metrics: hit / session / flow packet counts, alerts 
nsx-t firewall rule where   Security Group like  'ryan-hack-servers' order by  Hit Count 
firewall rules where source ip = 192.168.100.34 or destination ip = 192.168.100.34 
firewall rules where source ip = 123.123.123.123 and   Port = 3306
firewall rules where source ip = 123.123.123.123 and   Port = 3306 and  Source != ANY and  Destination != ANY
firewall rules where source ip = 123.123.123.123 and   Configured Service =  'MySQL_3306' 
NSX-T Firewall Rule where Configured Source Count  > 20 or Configured destination Count > 20
flow  where  firewall rule =  'r1' group by source security group, destination security group
	// add Source IP, Destination IP in more filters
NSX Policy Group   where Direct outgoing Rules like r1
flow  where  firewall rule =  'r1' group by  Security Groups 
flow  where  firewall rule =  'r1' group by  IP Address 
NSX Policy Group  where  Translated VM =  'Ryan-Victim-VM' 
NSX Policy Group   where  IP Address = 70.70.70.31
NSX Policy Group   where  IP Address =  70.70.70.31 group by Direct Incoming Rules
NSX Policy Group   where  IP Address =  70.70.70.31 group by Direct Outgoing Rules
```

Exporting DFW rules into CSV
```
https://docs.vmware.com/en/VMware-Aria-Operations-for-Networks/6.10/Using-Operations-for-Networks/GUID-FF803835-0409-4ACB-95AC-91428541C4CB.html?hWord=N4IghgNiBcIE4FcIFMAEyAeAHA9nALiAL5A
```
SHow me flows coming into NSX domain from a non NSX domain and which rules they are hitting, excluding some vm's and clusters
```
flows where  Source Manager  not in ( 'SC2nsxt-01.cmbu.local' , 'nsx-emea.vrni.cmbu.local' ) and  Destination Manager in (  'SC2nsxt-01.cmbu.local' ,  'nsx-emea.vrni.cmbu.local' ) and  firewall action = 'ALLOW'  and VM not in (vRNI-PREGA-Collector-1, vRNI-FieldDemo-Collector-1) and not in cluster 'North Cluster'  group by  firewall ruleid
flows where  Source Manager  not in ( 'SC2nsxt-01.cmbu.local' , 'nsx-emea.vrni.cmbu.local' ) and  Destination Manager in (  'SC2nsxt-01.cmbu.local' ,  'nsx-emea.vrni.cmbu.local' ) and  firewall action = 'DENY'  and VM not in (vRNI-PREGA-Collector-1, vRNI-FieldDemo-Collector-1) and not in cluster 'North Cluster'  group by  firewall ruleid
```
#### Lateral Threat, Internal Traffic <a name="lateral"></a>
```
plan security
plan security of application 'SAP'
show Flow where Flow Type = East-West group by  Subnet Network
show Flow where Flow Type = Switched group by  Subnet Network
show flows where  Flow Type =  'Same Host' group by  Subnet Network   
show flows where  Flow Type =  'Same Host' group by vm       
top 10 flows where  Source Country =  'Australia’ and  Destination Country !=  'Australia’ group by  Destination Country,  Source Country order by sum(bytes)
sum(Bytes), sum(Bytes Rate) of flows where (Flow Type = 'Routed' and Flow Type = 'Same Host')
flows where flow type = 'Source is internet' and port in (22,23,3389) group by Source Country
flows where flow type = 'Source is internet' and port in (22,23,3389) group by Source Country, Destination VM
flow where Destination Port == 3389 group by Destination VM, Source IP Address
vm where Incoming Port = 445 group by Operating System
flow where destination port name = 'dns' group by Destination VM
```

#### Change and Auditing <a name="audit"></a>
```
changes
problems
events
```

#### Managing NSX Domain <a name="nsxday2"></a>
```
NSX-V Manager 'wdcnsx-master.cmbu.local'
NSX-T Manager 'sc2vc05-vip-nsx-mgmt.cmbu.local'
NSX-T Security Group '
Edges: NSX-T Transport Node 'sc2nsxt-edge-01' 
edge Dataplane CPU Core Usage Rate of  NSX-T Edge Node CPU Core where  Edge Dataplane CPU Core Usage Rate > 0.1 %
show flows order by Average TCP RTT 
Average Physical Network Flow Latency 
show flows where Maximum TCP RTT > 150
flows in last 7 days   >> FLOW INSIGHTS >> NETWORK PERFORMANCE
others: https://vrealize.vmware.com/sample-exchange/vrealize-network-insight-search-exchange/categories/Firewall
router interface where Rx packet drops > 0    //troubleshoot uplink ports
NSX-T Logical Switch where Rx Packet Drops > 0       //troubleshoot segments
```
#### VMC  <a name="vmc"></a>

- Viewing your SDDC and associated NSX
```
VMC SDDC 'CMBU-TMM'
NSX Policy Manager '10.73.185.131'
```

- Defining or Discovering and viewing Applications
```
applications    //use hostname, SNOW, or even ML for Flow Based App Discovery
```

- Troubleshooting - Audit
```
event
changes
problems
```

- Troubleshooting - General
```
topn      //shopping list of issues
topn in VMC SDDC 'CMBU-TMM'    ////shopping list of issues in VMC
vm where SDDC Type = 'VMC'     //// pick one, >> METRICS >> ALL METRICS
```

- Troubleshooting - Edges
```
vm where name like 'NSX-Edge' and sddc type = 'VMC'  //NSX Edge VM in VMC provides the network metrics (Rx Packets, Tx Packets etc)  in the facets and view the metrics graph    // >> METRICS >> ALL METRICS
Rx packets of router interface where vrf = 'vmc'
Tx packets of router interface where vrf = 'vmc'
Total rx bytes of router interface
Total tx bytes of router interface
Rx Dropped Packets of router interface where vrf = 'vmc'
Tx Dropped Packets of router interface where vrf = 'vmc’
router interface where Rx Packet Drop Ratio > 10% and manager = '10.73.185.131’

```

- Troubleshooting - Hosts and VM's
```
show hosts where SDDC Type = 'VMC' 
show hosts where Total Packet Drop Ratio = 0 and SDDC Type = 'VMC' 
show hosts where Max Network Rate  and Rx Packet Drops and Tx Packet Drops  and SDDC Type = 'VMC' 
show hosts where Max Network Rate  and Rx Packet Drops and Tx Packet Drops  and Max Latency and Active Memory > 20 gb and Total Network Traffic and Bus Resets and SDDC Type = 'VMC' 
vnic count, cpu count of vms where SDDC Type = 'VMC'  order by CPU Usage Rate 
vmknic where Total Packet Drops > 0
Vnic where Total Packet Drops != 0
hosts where Total Packet Drops != 0
show vm where Rx Packet Drops > 0
show vm where Memory Usage Rate and Memory Balloon != 0
show vm where Memory Usage Rate > 80 order by memory usage rate
show vm where CPU Usage Rate > 80 order by CPU Usage Rate 
show vm where Total Packet Drops > 0 and Datastore like 'sc2c01vsan01' 
show flows where Lost Packet Ratio > 0
```

- Troubleshooting - Performance
```
show flows       //then Flow Insights >>  Network performance for NPM
flow by Average TCP RTT where SDDC = 'CMBU-TMM' 
flows where Source SDDC = 'CMBU-TMM'   // add side filter for TCP RTT and PORT 53
flows where src ip = 192.168.10.3 and dst ip = 172.16.43.56        //shows sec groups, hosts, rules applied to flow
```

- Security Policy
```
plan security
     // by default you view the wagon wheel as VLAN/VxLAN, if you use other groupings to view it, the FW recommendations are based on the grouping you’ve selected. 		If you have more groups (application constructs, security groups, anything) and then group the security planner with those, the recommendations will 		get narrower too.  Skin the security planning wheel via 'Group By' VM or Security Groups, the FW recommendations are defined in that way
plan security of cluster xxxx
plan security of vc manager   // DROPDOWN ‘FLOW TYPE’ > All Unprotected Flows 
plan security of application 'MyCRM'  //change 'GroupBy' to VLAN/VxLAN Segments - Security Groups etc
pci compliance of Cluster 'Cluster-1'
VMware VM 'Cloud_Machine_1-mcm647-135898688490'   // click flows below etc 
plan VMware VM 'Cloud_Machine_1-mcm647-135898688490' //security policy for a single VM
NSX Policy Group 'VMC-Compute-10.72.82.0/24'
Security Tag 'ST-FunBike-DB'
```

- Traffic Profiling and Measurments
```
show flows       //then Flow Insights 
      - View Top Talkers by Volume (GB), Rate (Gbit p/s), Session Count, and Flow Counts
      - Group by: VMs, Clusters, Segments, Security Groups, and more.
show flows       //then Flow Insights >>  Network performance for NPM
flows where Source SDDC = 'CMBU-TMM' and Destination SDDC = 'CMBU-TMM'  // >>pick a flow >> host
flows where application = 'MyCRM'
flows where Source SDDC = 'CMBU-TMM'   // add side filter for TCP RTT and PORT 53
flows where src ip = 192.168.10.3 and dst ip = 172.16.43.56        //shows sec groups, hosts, rules applied to flow
VMware VM 'xxxxxxx' to VMware VM 'yyyyyy'      //within VMC
VMware VM 'xxxxxxx' to VMware VM 'zzzzzz'       //back to on-prem via Dx
sum (bytes), sum(packets) of flows where source sddc = 'CMBU-TMM' and flow type = 'Destination is internet' 
max(series(sum(byte rate),300)) of flow where Destination SDDC not in ( 'CMBU-TMM' )
max(series(sum(byte rate),300)) of flow where source SDDC in ( 'CMBU-TMM' ) and Destination SDDC not in ( 'CMBU-TMM' )
series(sum(byte rate),300) of flow where Source SDDC = 'CMBU-TMM'  and Flow Type = 'East-West' 
flows where flow type = 'Direct Connect' group by Connection 
max(series(sum(Bytes)))of Flows where flow type = Direct Connect 
max(series(sum(packets)))of Flows where flow type = Direct Connect and group by Connection
```

- Connectivity
```
NSX Policy Segment where SDDC Type = VMC
VMware VM 'xxxxxxx' to VMware VM 'yyyyyy'      //within VMC
VMware VM 'xxxxxxx' to VMware VM 'zzzzzz'       //back to on-prem via Dx
VMC Direct Connect '7224-10.73.185.131'
```


#### Public Cloud  <a name="publiccloud"></a>
```
aws
aws EC2
aws vpc
aws Account 'AWS_879816619487'
aws VPC Peering Connection
aws Virtual Private Gateway
aws VPN Connection
plan AWS VPC 'vRNI-Demo'
azure
show flows where Azure Virtual Network 
```

- Path tracing in Cloud
```
AWS EC2 'vrni-tmm-lab-parse' to AWS EC2 'vrni-tmm-lab-parse-vpc2' 
```

- Flows inside Cloud
```
Flow where AWS VPC = 'vRNI-Demo' order by bytes
```

- Path tracing in Cloud
```
AWS EC2 'vrni-tmm-lab-parse' to AWS EC2 'vrni-tmm-lab-parse-vpc2' 
AWS EC2 'HIVE-Storage-Server'  to internet
```

#### VeloCloud <a name="velocloud"></a>
- Velo stuff collected from Edge UDP2055, and API to VCO, and VCG
```
VeloCloud Enterprise 'vRNI Field Demo'
VeloCloud Edge 'Detroit, Branch'
```

- Velo Flows up to 30 days
```
flow group by SDWAN Edge
flow group by Source SDWAN edge where Application like 'HIVE Training'
flow group by Source SDWAN edge where Application != 'HIVE Training'
show flows where Destination Application = 'HIVE Training' order by Source SDWAN edge  
```

- Time series graphs
```
series(sum(byte rate)) of flow where source application = 'HIVE Training' and SDWAN Edge = 'Rotterdam, Branch' 
```

#### Kubernetes <a name="k8s"></a>
- Where visibility gets really hard...
```
Kubernetes Dashboard
Kubernetes Namespace 'pks-system'
Kubernetes Cluster 'k8s-cluster-2'
Kubernetes Service 'carts'
```


## Traffic Analysis Queries <a name="queries"></a>

#### Traffic Analysis - L2 Network <a name="query-traffic-network"></a>
```
vms group by Default Gateway Router
vms group by Network Address, Default Gateway
L2 Network group by Default Gateway
L2 Network group by Default Gateway, Network Address
L2 Network where VM Count = 0
L2 Network where VM Count = 0 group by Network Address
L2 Network where VM Count > 0 group by Network Address, VM Count
Router Interface group by Device
Router Interface where device = 'w1c04-vrni-tmm-7050sx-1'
```

#### Traffic Analysis - Routing and Aggregation <a name="query-traffic-routing"></a>
- Flows by Subnet
```
flows group by subnet order by sum(bytes)
```

- Flows by Destination VM
```
flows group by Destination VM order by sum(bytes)
```

- Show highest VM->VM pairs by Byte Rate (Routed)
```
sum(bytes) of flows where Flow Type = 'Routed' group by Source VM, Destination VM order by avg(Bytes Rate)
```

- Show highest VM->VM pairs by Byte Rate (Switched)
```
sum(bytes) of flows where Flow Type = 'Switched' group by Source VM, Destination VM order by avg(Bytes Rate)
```

- Show highest Subnet->Subnet pairs by Byte Rate (Routed)
```
sum(bytes) of flows where Flow Type = 'Routed' group by Source Subnet, Destination Subnet order by avg(Bytes Rate)
```

- Show highest Subnet->Subnet pairs by Byte Rate (Switched)
```
sum(bytes) of flows where Flow Type = 'Switched' group by Source Subnet, Destination Subnet order by avg(Bytes Rate)
```

#### Traffic Analysis - Ports and Services <a name="query-traffic-services"></a>
- List VMs accepting UDP 53 (DNS) connections
```
list(Destination VM) of flows where Destination Port = 53
```

- List flows by port-range
```
flows where (port >= 100 AND port <= 200)
```

- Show RDP connections to VMs (List)
```
flows where Destination Port == 3389
```

- Show RDP connections to VMs from specific `Source Country`
```
flows where Destination Port == 3389 and Source Country == 'China'
```

- Show RDP connections to VMs (List VM pairs)
```
flows where Destination Port == 3389 group by Destination VM, Source VM
```

- Show RDP connections to VMs (List IP-VM pairs)
```
flows where Destination Port == 3389 group by Destination VM, Source IP Address
```

- Show RDP connections to VMs (List Source Country)
```
flows where Destination Port == 3389 group by Destination VM, Source Country
```

#### VMs, Routed via Specific L3 Device <a name="query-vms-routed-specific"></a>
- Show me all VMs that use L3 Router `w1c04-vrni-tmm-7050sx-1`
```
vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))
```

- Show me all VMs that use L3 Router `w1c04-vrni-tmm-7050sx-1` - group by VLAN
```
vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1')) group by VLAN
```

- Show me all VMs that use L3 Router `w1c04-vrni-tmm-7050sx-1` - group by VLAN, SUBNET
```
vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1')) group by VLAN, Network Address
```

- Show me all VMs that use any L3 Router - group by Router Interface, Network Address
```
vm group by Default Gateway Router Interface, Network Address
```

#### VM Flow Hairpinning and L3 Subnet Dependencies <a name="query-vms-hairpinning"></a>
- Show me traffic between VMs grouped by L3 router device
```
vms group by Default Gateway Router, Default Gateway order by sum(Total Network Traffic)
```

- Show me VM->VM pairs of flows hairpinning via any L3 Router
```
sum(Bytes) of flows where (Flow Type = 'Routed' and Flow Type = 'Same Host') group by Source VM, Destination VM order by avg(Byte Rate)
```

- Show me aggregated Bytes and Byte rate of hairpinning traffic
```
sum(bytes), avg(Bytes Rate) of flows where (Flow Type = 'Routed' and Flow Type = 'Same Host')
```

- Show me physical Hosts from where I am hairpinning traffic
```
flows where (Flow Type = 'Routed' and Flow Type = 'Same Host') group by Host order by sum(Bytes)
```

- Show me VM->VM hairpinning from a specific host
```
flows where host = 'esx003-ovh-ns103551.vrni.cmbu.org' and (Flow Type = 'Routed' and Flow Type = 'Same Host') group by Source VM, Destination VM order by sum(bytes)
```

#### Flows: Aggegration Prefix - Traffic Stats <a name="query-flows-aggregation"></a>
A useful query prefix for constructing aggregation traffic stats for `Flows`  
Replace **`<flow.query>`** with actual query filter syntax.  
```
sum(Bytes), sum(Bytes Rate), sum(Retransmitted Packet Ratio), max(Average Tcp RTT) of flows where <flow.query>
```

#### Flows: Routed, Same Host <a name="query-flows-routed-samehost"></a>
- Show me aggregated Bytes and Byte Rate of hairpinning traffic via L3 Router (includes VM->Physical flows)
```
sum(Bytes), sum(Bytes Rate) of flows where (Flow Type = 'Routed' and Flow Type = 'Same Host')
```

- Show me hosts from where I am hairpinning traffic (includes VM->Physical flows) - group by `Host`
```
sum(Bytes), sum(Bytes Rate) of flows where (Flow Type = 'Routed' and Flow Type = 'Same Host') group by Host order by sum(Bytes)
```

- Show me VM->VM pairs hairpinning traffic via any L3 Router in same Host
```
sum(Bytes), sum(Bytes Rate) of flows where (Flow Type = 'Routed' and Flow Type = 'Same Host') group by Source VM, Destination VM order by sum(Bytes)
```

- Show me VM->VM hairpinning via any L3 Router from specific host `esx003-ovh-ns103551.vrni.cmbu.org`
```
sum(Bytes), sum(Bytes Rate) of flows where host = 'esx003-ovh-ns103551.vrni.cmbu.org' and (Flow Type = 'Routed' and Flow Type = 'Same Host') group by Source VM, Destination VM order by sum(bytes)
```

#### Flows: Routed, VM->VM, via any L3 Router <a name="query-flows-routed-any"></a>

- Show aggregate traffic stats of all VM->VM flows via any L3 Router
```
sum(Bytes) of flows where (Flow Type = 'Routed' and Flow Type = 'VM-VM')
```

- Show aggregate traffic stats of all `Same Host` VM->VM flows via any L3 Router
```
sum(bytes) of flows where (Flow Type = 'Routed' and Flow Type = 'VM-VM' and Flow Type = 'Same Host')
```

- Show aggregate traffic stats of all `Diff Host` VM->VM flows via any L3 Router
```
sum(bytes) of flows where (Flow Type = 'Routed' and Flow Type = 'VM-VM' and Flow Type = 'Diff Host')
```

- Show aggregate traffic stats of `Same Host` VM->VM flows that are hairpinning via any L3 Router
```
sum(Bytes), sum(Bytes Rate), sum(Retransmitted Packet Ratio), max(Average Tcp RTT) of flows where (Flow Type = 'Routed' and Flow Type = 'VM-VM' and Flow Type = 'Same Host')
```

- Show me VM->VM pairs and traffic stats of `Same Host` VM->VM flows that are hairpinning via any L3 Router
```
sum(Bytes), sum(Bytes Rate), sum(Retransmitted Packet Ratio), max(Average Tcp RTT) of flows where (Flow Type = 'Routed' and Flow Type = 'VM-VM') group by Source VM, Destination VM order by sum(Bytes)
```

#### Flows: Routed, VM->VM via specific L3 Router <a name="query-flows-routed-specific"></a>
- Show me all flows via L3 Router `w1c04-vrni-tmm-7050sx-1` 
```
flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1')))
```

- Show me aggregate packet stats of all flows via L3 Router `w1c04-vrni-tmm-7050sx-1`
```
sum(Bytes), sum(Bytes Rate), sum(Retransmitted Packet Ratio), max(Average Tcp RTT) of flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1')))
```

- Show me all flows (East-West + North-South) via L3 Router `w1c04-vrni-tmm-7050sx-1`
```
sum(bytes) of flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))) AND (Flow Type = 'Routed')
```

- Show me all North-South (VM->Internet) flows via L3 Router `w1c04-vrni-tmm-7050sx-1`
```
sum(bytes) of flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))) AND (Flow Type = 'Routed' and Flow Type = 'Internet')
```

- Show me all East-West (VM->VM and VM->Physical) flows via L3 Router `w1c04-vrni-tmm-7050sx-1`
```
sum(bytes) of flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))) AND (Flow Type = 'Routed' and Flow Type = 'East-West')
```

- Show me all VM->VM flows via L3 Router `w1c04-vrni-tmm-7050sx-1`
```
sum(bytes) of flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))) AND (Flow Type = 'Routed' and Flow Type = 'VM-VM')
```

- Show me all VM->Physical flows via L3 Router `w1c04-vrni-tmm-7050sx-1`
```
sum(bytes) of flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))) AND (Flow Type = 'Routed' and Flow Type = 'VM-Physical')
```

- Show me VM->VM pairs and traffic stats of all flows via L3 Router `w1c04-vrni-tmm-7050sx-1` 
```
sum(Bytes), sum(Bytes Rate), sum(Retransmitted Packet Ratio), max(Average Tcp RTT) of flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))) group by Source VM, Destination VM order by sum(Bytes)
```

- Show me SUBNET->SUBNET pairs and traffic stats of all flows via L3 Router `w1c04-vrni-tmm-7050sx-1` 
```
sum(Bytes), sum(Bytes Rate), sum(Retransmitted Packet Ratio), max(Average Tcp RTT) of flows where vm in (vms where Default Gateway Router Interface in (Router Interface where (device = 'w1c04-vrni-tmm-7050sx-1'))) group by Source Subnet, Destination Subnet order by sum(Bytes)
```

#### Moving, Migrating Applications <a name="migration"></a>
When doing multiple applications and forming Move Groups, create a parent container application called ‘Move_Group_1’ and make the specific applications a part of it. Then use the group name in the below searches. Ref: https://cloud.vmware.com/community/2019/12/10/planning-application-migration-vmware-cloud-aws-vrealize-network-insight-cloud/

- Show application bandwidth

https://blogs.vmware.com/cloud/2019/12/10/planning-application-migration-vmware-cloud-aws-vrealize-network-insight-cloud/

```
Application 'HIVE Training'
vm where name like web
series(sum(bytes rate)) of Flows where Application = '3TierApp02'
 #(can change to last 3 days, or last 30 days for instance, and click search again)
series(sum(network usage)) of  VMware VM where  Name like web
series(sum(bytes rate)) of flow where vm  like 'web'
sum(Total Traffic) of Flows where Application =  'HIVE Training' in last 7 days
sum(Total Traffic) of Flows where Application =  'HIVE Training' in last 24 hours
sum(Total Traffic) of Flows where source Application =  'HIVE Training' and  Destination Application = ‘mybackup-app’ in last 30 days
sum(Total Traffic) of Flows where  Destination VM = 'mybackup-vm' in last 7 days
sum(Total Traffic) of Flows where source Application =  'HIVE Training' and   Destination VM = 'mybackup-vm' in last 30 days
```

- Show application which contain a particular VM
```
Applications which contain a particular VM
Applications where Virtual Member = "shopping-db"
Applications where Virtual Member like DB
```


- Show application maximum flow rate
```
max(series(sum(flow.totalPackets.delta.summation.number))) of flow where source application =  'HIVE Training'
```

- Show incoming application traffic
```
series(sum(byte rate),300) of flow where destination application = ‘‘Move_Group_1'
max(series(sum(byte rate),300)) of flow where destination application = ‘Move_Group_1’
Get outgoing traffic by substituting destination with source.
```

- Show applications consuming vlan 10 so phy fw's and phy LB's can be coordinated
```
application where ip endpoint.network interface.L2 Network = 'vlan-10' 
```

- How much resource does the app take?
```
sum(CPU Cores), sum(Memory Consumed) of VMs where application = 'Migration Wave 1'
vm where L2 Network = '10.72.82.0/24' group by Virtual Disk Capacity
vm where  Application = 'MigrationWave01' group by  Virtual Disk Capacity 
Virtual Disk of VMware VM where Application =  'HIVE Training'
sum(Used Space) of datastore where  VM like '3TierApp01-DB-VM01' 
vm where  L2 Network = 'APP-LS'
 #into these commands
sum(Used Space) of datastore where  VM in ( '3TierApp02-App-VM01' , '3TierApp02-App-VM02' )
sum(Free Space) of datastore where  VM in ( '3TierApp02-App-VM01' , '3TierApp02-App-VM02' )
```

- Show internet traffic
```
series(sum(byte rate),300) of flow where source application = ‘Move Group 1' and flow type = 'Destination is Internet’
max(series(sum(byte rate),300)) of flow where destination application = ‘Move_Group_1’
Get outgoing traffic by substituting destination with source.
```

- Show packets p/s to internet
```
series(sum(flow.totalPackets.delta.summation.number),300) of Flow where source Application like 'Move_Group_1' and Flow Type = 'Destination is Internet' 
max(series(sum(flow.totalPackets.delta.summation.number),300)) of Flow where source Application like 'Move_Group_1' and Flow Type = 'Destination is Internet' 
Get outgoing traffic also by substituting destination with source.
```

- Show traffic to remaining on-prem apps
```
series(sum(byte rate),300) of flow where application = 'Move_Group_1' and Flow Type = 'East-West' 
```

- Which Operating Systems are out there
```
vm group by  Operating System
vm where Incoming Port = 445 and Operating System like 'Microsoft Windows 10 (64-bit)' 
vm where Incoming Port = 445 group by Operating System
```
#### Virtual Network Assessment <a name="vna"></a>
Analyses Traffic Patterns to ascertain E/W flows and flows which may happen solely with a security zone, which often has has no security visiblity and / or enforcement., thus presenting, a pivot point or later move for an attacker.

[[https://blogs.vmware.com/cloud/2019/12/10/planning-application-migration-vmware-cloud-aws-vrealize-network-insight-cloud]

```
Identify is customer using a fwd proxy as N/S % flows will be distorted, if so, enter it as N/S destination in settings
Use application definition to identify DEV, or even better additionally PROD and Crown Jewel DB groupings so we can see incoming flows
or just manually create an app group 'custom vm search' name like dev
vm where name like DEV
vm where name like SQL
top50 flows where destination country != 'Australia' group by source vm, destination country order by sum(Bytes) in last 30 days
flows where source application = 'PROD' and destination application = 'DEV' or source application = 'DEV' and destination application = 'PROD'
flows where source application = 'DEV' and destination application != 'DEV'
flows where flow type = 'source is internet' and port in (22,23,3389) group by source country, destnation vm
flows where flow type = 'destination is internet' in last 30 days group by application
flows where flow type = 'source is internet' in last 30 days group by application
flows where source application = 'DEV - ALL' and destination application != 'DEV - ALL' in last 30 days
plan application 'CrownJewelDB'
flows where port = 3389 group by application
flows where port = 3389 and destination application = 'CrownJewelDB' in last 30 days
flows where destination port = 3389 and destination application = 'CrownJewelDB' in last 30 days
```

## Using vRNI via its API <a name="api"></a>
Step by step instructions for setting up postman and interacting with vRNI's OpenAPI spec

![API method](https://github.com/defaultroute0/vrni/blob/master/images/image.png?raw=true)

https://github.com/vrealize-network-insight/vrni-api-postman-collection

Import these two files as raw github links / URLs into postman
```
https://raw.githubusercontent.com/vrealize-network-insight/vrni-api-postman-collection/master/vrni-6.5.0-api-postman-collection.json
https://raw.githubusercontent.com/vrealize-network-insight/vrni-api-postman-collection/master/vrni-6.5.0-api-postman-environment.json
```
![API method coming soon](https://github.com/defaultroute0/vrni/blob/master/images/postmancollection.png?raw=true)

Set the “host” parameter in environment as your vRNI setup IP.
![API method coming soon](https://github.com/defaultroute0/vrni/blob/master/images/postmanenv.png?raw=true)

Leave parent auth method as no auth for collection
This collection has an auth folder. In the “Create an auth token” call, change the body with the vRNI login credentials and you will get the token.

Either use my LDAP one pictured below, or just use LOCAL example

```
                      "username": "admin@local",
                      "password": "testpassword",
                      "domain": {
                       "domain_type": "LOCAL"
```

Create an auth token
![API method coming soon](https://github.com/defaultroute0/vrni/blob/master/images/createauthtoken.png?raw=true)	      
		      
Come back to vrni env collection and change the token param manually to the newly returned token you got (my example as pictured above)
or
place this code in 'Tests' section of postman for the POST
```
var responseJson = JSON.parse(responseBody);
postman.setEnvironmentVariable("AuthenticationToken", responseJson.token);
```		      
	
![API method coming soon](https://github.com/defaultroute0/vrni/blob/master/images/autotoken.png?raw=true)
		
Then you can send API calls into vRNI while the token lasts for the whole collection

Create PIN board example, noting ‘id’
![API method coming soon](https://github.com/defaultroute0/vrni/blob/master/images/createpinboard.png?raw=true)

Then using PINboard  ID in env param to set some content
![API method coming soon](https://github.com/defaultroute0/vrni/blob/master/images/createapin.png?raw=true)

Hope this shows you a quick example of way you can drive pinboards and their content for specific users via API method

You can see OpenAPI spec documentation live in the product here:
![API method coming soon](https://github.com/defaultroute0/vrni/blob/master/images/openapispec.png?raw=true)

## Import/Export Applications <a name="applications"></a>
Step by step instructions for setting up and exporting vRNI Application definitions as per:  
https://code.vmware.com/samples/7128/backup-and-restore-applications---vrealize-network-insight

This workflow leverages the vRNI Python SDK.  

#### 1. Create new Centos VM
Build a new minimal Centos VM to run the necessary scripts.  
For this, you can use APNEX's unattended install procedure here:  
https://github.com/apnex/pxe

#### 2. Install Python and pre-requisite packages
Each command should be completed individually before proceeding to the next.  
Commands assume you are logged in as root.  
```sh
yum update
yum install epel-release
yum install python python-pip git
pip install --upgrade pip
pip install python-dateutil urllib3 requests pyyaml
```

#### 3. Clone the `network-insight-sdk-python` repository
```sh
git clone https://github.com/vmware/network-insight-sdk-python
```

#### 4. Install the Python Swagger client
```sh
cd network-insight-sdk-python/swagger_client-py2.7.egg
python setup.py install
```

#### 5. Test and run an example
```sh
cd ../examples
python application_backups.py --help
```

#### 6. EXPORT: Run `application_backups.py` with valid parameters
Example with **LOCAL** auth:
```sh
python application_backups.py \
--deployment_type 'onprem' \
--platform_ip '<vrni.fqdn.or.ip>' \
--domain_type 'LOCAL' \
--username '<username>' \
--password '<password>' \
--application_backup_yaml 'applications.yaml' \
--application_backup_action 'save'
```

Example with **LDAP** auth:
```sh
python application_backups.py \
--deployment_type 'onprem' \
--platform_ip '<vrni.fqdn.or.ip>' \
--domain_type 'LDAP' \
--domain_value '<domain>' \
--username '<username@domain>' \
--password '<password>' \
--application_backup_yaml 'applications.yaml' \
--application_backup_action 'save'
```

#### 7. IMPORT: Run `application_backups.py` with valid parameters
Example with **LOCAL** auth:
```sh
python application_backups.py \
--deployment_type 'onprem' \
--platform_ip '<vrni.fqdn.or.ip>' \
--domain_type 'LOCAL' \
--username '<username>' \
--password '<password>' \
--application_backup_yaml 'applications.yaml' \
--application_backup_action 'restore'
```

Example with **LDAP** auth:
```sh
python application_backups.py \
--deployment_type 'onprem' \
--platform_ip '<vrni.fqdn.or.ip>' \
--domain_type 'LDAP' \
--domain_value '<domain>' \
--username '<username@domain>' \
--password '<password>' \
--application_backup_yaml 'applications.yaml' \
--application_backup_action 'restore'
```

#### Throttling Calls - HTTP 429 Errors
Depending on vRNI platform utilisation and deployed size, yoou may see a `429 Too Many Requests` error.  
This is the platfrom appliance rejecting API calls that exceed its current ability to process.  

Solve this by modifying the `application_backups.py` file to sleep longer (for 1 second) between API calls.  

```diff
-    36	                time.sleep(0.025)
+    36	                time.sleep(1)
-    58	                time.sleep(0.025)
+    58	                time.sleep(1)
```
