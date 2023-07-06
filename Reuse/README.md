Imports for reuse within a Python project are a bit painful.

There are several ways to handle them.

The recommended approach is to use the following command:

```
pip install --editable <path>
```

Examples:

```
pip install --editable C:\Users\Dave.Mauney\PycharmProjects\Automation
```
or

```
cd C:\Users\Dave.Mauney\PycharmProjects\Automation
pip install --editable .
```

This keeps the code using the package simple, and it works for PyCharm (which handles relative imports easily anyhow) and the command line (which does not handle relative imports).
It allows you to run a script from the current folder rather than forcing you to always run from the project root folder, which is somewhat burdensome.

For PyCharm, in the project tree, right click on the folder above "Reuse", select "Mark Directory as" and select "Sources root".

A second approach, that is not recommended, is to add a path in the module doing the relative import like:

sys.path.append("../..")

This is painful for several reasons:

1. It is not the recommended/pythonic way of doing it
2. It will violate PEP 8, so you will get a warning of "PEP 8: E402 module level import not at top of file"
3. The path needs to be set relative to where the module doing the import runs

A third technique, which is also not recommended, is to modify the PYTHONPATH.

More details on why these techniques are not recommended can be found [here](https://stackoverflow.com/questions/68033795/avoiding-sys-path-append-for-imports)