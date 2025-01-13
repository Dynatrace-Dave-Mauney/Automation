The following changes allow for locking down ActiveGates to perform:  

* Only agent routing  
* Only extension processing  

And facilitate adding an ActiveGate group and/or Network Zone.  

Linux default configuration file path:  
/var/lib/dynatrace/gateway/config  

Windows default configuration file path:  
%PROGRAMDATA%\dynatrace\gateway\config  

Modify or replace custom.properties with contents of  
* AllowOnlyMsgRouter-custom.properties - to allow only agent routing  
* AllowOnlyExtensions-custom.properties - to allow only extension processing  

To add an ActiveGate Group, update the [collector] section to include the contents of ActiveGateGroupExample.properties. 
Be sure to include only one "[collector]" stanza. 

To add a NetworkZone, append the contents of NetworkZoneExample.properties  

[Configuration properties and parameters of ActiveGate
](https://docs.dynatrace.com/docs/shortlink/sgw-configure)