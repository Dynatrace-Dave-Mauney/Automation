How To Update Host and/or Host Group Auto Update Settings using Python Modules

First, set up a virtual environment so the dependencies for the "Auto Update" project are kept separate from those of the ActiveGate:

    pip install virtualenv

Make an "autoupdate" project directory:

    mkdir -p /opt/dynatrace-managed/automation/python
    cd /opt/dynatrace-managed/automation/python

Make a separate environment

    python3 -m venv autoupdate

Activate the environment:

    source autoupdate/bin/activate

For more details About Python Environments:

    https://realpython.com/python-virtual-environments-a-primer/

Copy source code to that folder:

    cd /opt/dynatrace-managed/automation/python/autoupdate

    copy the following Python Modules extracted from the provided zip file

    autoupdate_settings_from_yaml.py
    generate_autoupdate_settings_yaml_from_xlsx.py
    report_autoupdate_settings.py

Replace any "env" or "token" values needed in these Python modules as needed

Install the dependencies for the Python modules:

    The easiest way to handle dependencies is to run the module and see "what it complains about".

    Then add the missing library:

    Example:

    pip install requests

    You might also try this command to add all the dependencies:

    pip install json requests ssl xlsxwriter yaml

    If you get a "Could not find a version that satisfies the requirement" for any particular library, it likely does not
    need to be installed and can be removed from the command above.

To Run Manually:

    cd /opt/dynatrace-managed/automation/python/autoupdate

    # Generate an excel spreadsheet of host groups, hosts, versions and report them
    python3 report_autoupdate_settings.py

    # Modify the spreadsheet by adding "H" or "HG" to the "Scope" column and "DISABLED" or "ENABLED" or "INHERITED" to the "Setting" column for each host group and/or host to be modified.
    python3 report_autoupdate_settings.py

    # Generate the "autoupdate.yaml" file from the previously modified spreadsheet.
    python3 generate_autoupdate_settings_yaml_from_xlsx.py

    # Perform the changes specified in the "autoupdate.yaml" file.
    python3 autoupdate_settings_from_yaml.py
