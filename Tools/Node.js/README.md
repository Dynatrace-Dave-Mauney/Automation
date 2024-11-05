# Overview

The goal of this project is to use Node.js as a tool where it makes sense with Dynatrace.

The "RUMJS" sub project has it's own README.md.

If you get errors with dependencies, you may need to run npm install commands like:

npm install http
npm install node:fs
npm install js-yaml
npm install json

# Command Line Notes
node_verion.bat
node --version

Note: Running the "logger" modules requires that you redirect console output to a file (as done below) for the log to be ingested into Dynatrace.

run_fancy_json_logger.bat
node fancy_json_logger.js > /Temp/fancy_json_logger.log 2>&1

run_simple_console_logger.bat
node simple_console_logger.js > /Temp/simple_console_logger.log 2>&1


