# Overview

The goal of this project is to facilitate Dynatrace OneAgent SDK testing.  

Basically, it is just a download and expand of the Dynatrace OneAgent SDK with this documentation page added.  

To install the OneAgent SDK for Node.js:  

```
npm install --save @dynatrace/oneagent-sdk
```

To run an example, cd to the directory containing the Javascript file you want to try and run the appropriate node command to invoke it:  

```
cd OneAgent-SDK-for-NodeJs-main/samples/CustomRequestAttributes
node CustomRequestAttributesSample.js
```

If you get errors with dependencies, you may need to run npm install commands like:  

```
npm install http
```

Look at the port used by the sample (8001 or 8002, typically) and access that port on your host:    

http://localhost:8002/  
http://localhost:8001/  

# Documentation/How To Download the OneAgent SDK
[OneAgent SDK](https://docs.dynatrace.com/docs/shortlink/oneagent-sdk)  
[OneAgent SDK for Node.js](https://github.com/Dynatrace/OneAgent-SDK-for-NodeJs)  

The first documentation page covers all the technology we support for the OneAgent SDK.  
The second is specific to Node.js.  

To download from Github, use the green "Code" button.  You can then use "Download ZIP" if you are not a frequent git user, or you can clone the project if you are familiar with git.  

