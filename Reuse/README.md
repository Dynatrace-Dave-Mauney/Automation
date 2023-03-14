Imports for reuse within a Python project are a bit painful.

There are several ways to handle them.

Preferred:
pip install --editable <path>

Examples:
pip install --editable C:\Users\Dave.Mauney\PycharmProjects\Automation

cd C:\Users\Dave.Mauney\PycharmProjects\Automation
pip install --editable .

This keeps the code simple and works for PyCharm (which handles relative imports easily anyhow) and the command line (which does not handle relative imports).
And it allows you to run any script from its current folder rather than forcing you to always run from the project root folder, which is burdensome.

Otherwise, another way that is not recommended is to add a path in the module doing the relative import like:

sys.path.append("../..")

This is painful for several reasons:

1. It is not the recommended/pythonic way of doing it
2. It will violate PEP 8, so you will get a warning of "PEP 8: E402 module level import not at top of file"
3. The path needs to be set relative to where the module doing the import runs

Another, not recommended, approach is to modify the PYTHONPATH.

More details on why these techniques are not recommended can be found [here](https://stackoverflow.com/questions/68033795/avoiding-sys-path-append-for-imports)