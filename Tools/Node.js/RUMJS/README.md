# Overview

The goal of this project is to facilitate Dynatrace JavaScript Sample testing.

Basically, there is a very simple web server (server.js) that will serve the index.html file used by the verion of Dynatrace JavaScript indicated on the folder name.

To use another version, simply download and expand it and add a copy the server.js file to the "samples" subdirectory.

To run, cd to the directory containing "server.js" (cd dynatraceapi-1.301.5.20241007-103824/samples, for example) and run this command:

node server.js

If you get errors with dependencies, you may need to run npm install commands like:

npm install http
npm install node:fs

# Documentation
[JavaScript API](https://www.dynatrace.com/support/doc/javascriptapi/interfaces/dtrum_types.DtrumApi.html)


# How To Download the Samples

This is much more complex than it should be IMO, but do this:

[Offical Instructions](https://docs.dynatrace.com/docs/shortlink/api-rum#documentation)
See the "Offline RUM JavaScript API guide" tab which states:

To download the RUM JavaScript API guide from your environment

In Dynatrace, go to Settings > Web and mobile monitoring > Advanced setup.
Under JavaScript tag API, select Download documentation and samples.

An Example Link:
https://dad74988.live.dynatrace.com/#settings/rum/advancedsetup;gf=all

Just change the SaaS Tenant...