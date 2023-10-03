"""
NOTE:
    This module uses a non-public technique to extract the schema id from an object id.

    This technique is subject to failure at some point due to any change with the underlying encoding.
"""

import base64
import binascii

from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'NonProd'
# env_name_supplied = 'Prep'
# env_name_supplied = 'Dev'
# env_name_supplied = 'Personal'
# env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

warning_statement = '''This module uses a non-public technique to extract the schema id from an object id.
This technique is subject to failure at some point due to any change with the underlying encoding.
'''

# Customer 2 SLOs (test with "TU")
# test_update_object_ids = [
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOGMzZDVmNjUtNDRmNy0zMTRhLThlOTctZDVkNmUyMWViYWU3vu9U3hXa3q0'
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNzViYjhkMmYtNDliOS0zYTMzLWJjMzMtMzA3MWE4MTk2MGZhvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkODkxNDQ0YzMtMWIwNi0zOTk3LTliMzItYmIzODhmYjA2ZTEyvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOGE2NDdlNjUtYzU0MC0zM2JkLTlmOTQtNzY2YzZhZmIyMWRmvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOGIyYzZlYjQtNTViNS0zZGEzLWExM2YtNDJiYWVlZGIyY2Flvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOTE1Nzc1OTMtMmE1Ny0zZTZmLTg3OWYtMTg5YzdkOTg5MGUzvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOTMzOThmOWItYmRiMS0zYzMwLWFjMWUtYmYxZDQyMWY5Yjgyvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOTM3MGUzNGUtYzczMy0zNTlhLWExMGEtYjA2NGEzZmQzODUxvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOTgxNThhMzktZWM4Zi0zNjU5LWIyNjgtOWQwOWZhZDkwOGU4vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOTljNGNmY2UtZmJmOC0zZWNlLTljMWMtNGUwYjI3NmY3NjY3vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOWJmY2YzZGEtOWZiNy0zYjk0LWExZWYtNzg1ZWQ3NjBkODRmvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOWYyZTdiZDgtNWMwZC0zMWQ2LTg3OGUtNWE1MzUzNDg5MTEzvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkYTE0MjRhYzktOWYzZS0zNGEzLWIyMGUtMTU0ZTVjYTFjMzFmvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkYTMxODgwYjktMjQ3NC0zYzNmLTk4OWQtMjc0YjExN2RiOTg1vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkYTcxMTQwZWEtNDNjOS0zN2ZjLWE5NzctMTIyMzBhNzVkNjhjvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkYTg3YmY5YzctMDA3YS0zNzk1LTkzZWYtYzhkOWYyOWViZmIxvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkYTk2YTEzMmEtM2UwOS0zYjlmLTllYjgtODIxM2NjNTk3Zjljvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkYzNkNTRmMGQtOGRjNy0zMTM3LWE1MzMtMmYzOWRhYTU1NGFkvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkYzc5ZmMyMDQtNTNkYy0zMTk4LTljYTUtMjc1MGJhOTQ0Yzg5vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkYzgyZTUxM2EtYjU3YS0zN2UzLWI1OGYtZTZkOWEyYjlmNDJivu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkZGQ2MjM5MDQtNWM2ZS0zMzA1LWEyNjUtN2NjMzUzZjc2N2Rkvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkZTE0MzEwNDMtZThjMi0zMzg1LWJjNmYtYmUwMzg2NzRmNTMwvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkZWJkZGU4MzYtOGNhMy0zMzM1LTgyMzAtOGRlYzQxODI1N2I0vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkZjU4NDFjMmUtY2E0My0zZDVhLWI2MjQtOTU5MGY5ZDUxZjc4vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkZjVlZWJjMDQtMzVjYS0zMGNhLThjMDEtODAzZmY1Y2QxZWUwvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkZmU3ZTQzMzgtMDAxYy0zYzA3LTliYjQtMmQ0MTMyYTA1MTdivu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMDJjMWRiM2ItZDEzZC0zMDc4LWE0OWItZjc2MWRhM2YzMWRivu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMDMwYTRkNzUtOTVhNy0zZGUzLTk0MGEtMGUyYWNjM2FlYTYyvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMGYxZmUyZTgtOTA1Ny0zMzk0LTlkYmItN2M3MTdkZDFiMjIwvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMTdhNWUwZjgtOWRlNy0zMjU2LTlhN2EtODQ5N2RhNmUwZjlivu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMWMyMTQyNDUtMjZmZi0zYThmLTg2NTItN2ZmNmY0MWVkYjg5vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMWUzODI4NTctOTk3YS0zNmVkLTllYTktZjI2YTY0ZDEyYzI0vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMjMzMTU1ZGItZGJhYy0zNThiLTgyNmUtN2U3NTZiZWI4NTM2vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMjRkNzRhZjUtNmIyNC0zNjA3LWIzNjQtMzVjNDk2ODYyMDE0vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMmI3NjA2ZjEtNTIyOS0zMGJiLTk3MTEtMjkxYmI0ZTFjNmQzvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMmUzZGQ4MjMtMmNiNy0zNDY1LWFlMmMtNDQ0N2Y1NWY4ZGRkvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMmZiN2JjOWEtMTU0OS0zYjczLTkxNjgtNjk2MmM4M2IwZmY3vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMzA0OTNhYzktM2QwNy0zYWE3LTk0ODMtYzgxOTI0YWVlZTNivu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMzE5MmQ5NzQtMWQxMy0zNmZhLTkyODYtZmY5YWJiMTFiZWYxvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMzFhNTc3ZGQtOGIyZi0zNDc0LWE5MDEtYjQ4NjYzYjUwZmZivu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkMzNlZmRmYmItYjQ1YS0zZjRlLThkMzYtNmUxMTJkNzA4NjZmvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkM2I3N2U4ZWEtZjQ0Ny0zOTcwLWE5MzgtMDE0Y2Q4MGJkYWZkvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNGRhOWFlODEtZWY3NS0zYzdiLTg0MmEtNDk2MTkyODlkMzc5vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNTI0MzZlMGYtYzhlZC0zMTU1LTlhZmEtM2Y5ODkwYzhlNGZivu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNWMwYmI0NjYtODU2MC0zZDQxLWFkNzctYWE0MzJiMzVjOGFlvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNjAzNDA2ZTYtMTU4Zi0zZmEyLTlhNGYtMjJkZDk0YjA2MDY4vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNjA1ZGUzYzUtOGE1Ny0zNzJjLTk4MDYtMGM2YWYyNTE1NmQ5vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNjUxYTY3ODMtNmVhNS0zYzU0LWI3MTktNjY1ZDI2ZjNkNWYzvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNjllZDQ2YTUtZTQ0Mi0zZmY0LWI0ZmUtNDY3Njg4MGYwNjZmvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNmI1YWY1YjQtMjMzMy0zN2Y5LWJkNDktZjk2ZGZkNDgxZjg3vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNmNkYzA3NjQtY2YxMi0zNDgyLTg1MTQtZDc0MGY3NDA3NzFkvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNzRkNTkzMDctYWQ2Mi0zZGY4LTkxN2ItM2UzN2Q1MTUxNzVmvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNzYwZTllNjItMGY0My0zNDEyLTkyZjUtYzNjNzY2NWRlNjkyvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNzZjZDM0NzEtOGI4Zi0zY2EzLTlhMzMtYWQ1NGFjZGE0MTE0vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkNzczNTA0OWQtMjJiNS0zNTNiLThlNGItMTQwMTMzNTg5MTg1vu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkN2M1NGRlMzktOTEzYS0zZDQ5LWFiODUtOTBhNThjN2U2OTBivu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkN2QyZjk5NjItMzAwZC0zMmVmLTk3MGMtNGFlYTI5OTAyMGZjvu9U3hXa3q0',
#     'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkN2Q5YzU2ODAtMDlhZi0zMTQwLWJhNTItNTFjMmVlNWU0Yjhivu9U3hXa3q0',
# ]

test_update_object_ids = [
    'vu9U3hXa3q0AAAABABZidWlsdGluOm1vbml0b3Jpbmcuc2xvAAZ0ZW5hbnQABnRlbmFudAAkOGMzZDVmNjUtNDRmNy0zMTRhLThlOTctZDVkNmUyMWViYWU3vu9U3hXa3q0'
]

test_object_ids = [
    'vu9U3hXa3q0AAAABAB5idWlsdGluOm9zLXNlcnZpY2VzLW1vbml0b3JpbmcABnRlbmFudAAGdGVuYW50ACQ3M2I0YjA0Zi1iODExLTMxNDItYjg2Yy1mOTZiYjg2N2FlNjO-71TeFdrerQ',
    'vu9U3hXa3q0AAAABABZidWlsdGluOnNwYW4tYXR0cmlidXRlAAZ0ZW5hbnQABnRlbmFudAAkM2JmNzdmYjItZDY0Ni00YjczLTljNmYtNDMxNjBiMzQ2MTJjvu9U3hXa3q0',
    'vu9U3hXa3q0AAAABABhidWlsdGluOmFsZXJ0aW5nLnByb2ZpbGUABnRlbmFudAAGdGVuYW50ACQ0MDlhNGYyOC1mNDk2LTNhODQtOWNiNy00ZTQ0ZWQxYTZjMza-71TeFdrerQ',
    'vu9U3hXa3q0AAAABABhidWlsdGluOnJ1bS5ob3N0LWhlYWRlcnMABnRlbmFudAAGdGVuYW50ACQ1NTZmZTA0Zi0zYTE2LTM1ODgtYTkzOC02NzAyMDI4MjcwZWa-71TeFdrerQ',
    'vu9U3hXa3q0AAAABABlidWlsdGluOm9uZWFnZW50LmZlYXR1cmVzAAZ0ZW5hbnQABnRlbmFudAAkM2E3ZDM3NWMtOGNiZi0zZDE2LWJjODMtMjQwYTY0MzBhZWZivu9U3hXa3q0',
    'vu9U3hXa3q0AAAABABlidWlsdGluOnNwYW4tZW50cnktcG9pbnRzAAZ0ZW5hbnQABnRlbmFudAAkNTBjNDIyOTQtYjU3NS0zYzZjLWFjYTYtMTQ2MTNhMjM4NTMyvu9U3hXa3q0',
    'vu9U3hXa3q0AAAABABpidWlsdGluOnJlc291cmNlLWF0dHJpYnV0ZQAGdGVuYW50AAZ0ZW5hbnQAJGNmYTIxZDhjLWQ3Y2UtM2U2ZS1hZWUzLWMxMTc4NDI5MDkyY77vVN4V2t6t',
    'vu9U3hXa3q0AAAABABxidWlsdGluOmFwaXMuZGV0ZWN0aW9uLXJ1bGVzAAZ0ZW5hbnQABnRlbmFudAAkMDNiZWJiMzUtNjc4ZC0zNmJiLWI1YmMtZDAzNjUyNGQ0MDQ3vu9U3hXa3q0',
    'vu9U3hXa3q0AAAABABxidWlsdGluOnJ1bS5pcC1kZXRlcm1pbmF0aW9uAAZ0ZW5hbnQABnRlbmFudAAkMTE1Yzk2Y2QtMWNhZC0zMDU1LTk3OTQtOTBjMWQxOGUyZjQxvu9U3hXa3q0',
    'vu9U3hXa3q0AAAABABxidWlsdGluOnNwYW4tZXZlbnQtYXR0cmlidXRlAAZ0ZW5hbnQABnRlbmFudAAkNGMwYjk3NjAtYzE0My00MjExLTgxOGItMzk1NGJiY2ZiOTFlvu9U3hXa3q0',
    'vu9U3hXa3q0AAAABAC1idWlsdGluOmxvZ21vbml0b3JpbmcudGltZXN0YW1wLWNvbmZpZ3VyYXRpb24ABnRlbmFudAAGdGVuYW50ACQ4NWJmY2FkZi03ZDNhLTMxMDQtYWE1Yy0wNDM1MmUzZDY3M2O-71TeFdrerQ',
    'vu9U3hXa3q0AAAABACBidWlsdGluOmxvZ21vbml0b3JpbmcubG9nLWV2ZW50cwAGdGVuYW50AAZ0ZW5hbnQAJDZiMzg3MzJlLThkZGEtNDFjYS1hZTY2LTFkNzU2MjgyNzgyZr7vVN4V2t6t',
    'vu9U3hXa3q0AAAABACJidWlsdGluOmFub21hbHktZGV0ZWN0aW9uLnNlcnZpY2VzAAdTRVJWSUNFABA1MkFDNjI0RDcwQzM3N0JDACQ2MzA0NmViZC04OGNhLTNjNDgtYWI2MS03ZjE1Yzg2ZWNkNWa-71TeFdrerQ',
    'vu9U3hXa3q0AAAABACZidWlsdGluOm1vbml0b3JlZGVudGl0aWVzLmdlbmVyaWMudHlwZQAGdGVuYW50AAZ0ZW5hbnQAJDAzMGFkNGQyLTFlZDgtMzM0Yy1iM2QzLTkyYTA4MWVmNDJiZb7vVN4V2t6t',
    'vu9U3hXa3q0AAAABACdidWlsdGluOmxvZ21vbml0b3JpbmcubG9nLWJ1Y2tldHMtcnVsZXMABnRlbmFudAAGdGVuYW50ACQwMDQ4NzRlNC0wNWQwLTM2MjYtOGMzMC1hMDkxNmVmYzFiZTK-71TeFdrerQ',
    'vu9U3hXa3q0AAAABAClidWlsdGluOmJpemV2ZW50cy1wcm9jZXNzaW5nLWJ1Y2tldHMucnVsZQAGdGVuYW50AAZ0ZW5hbnQAJDk1MTA1NWVkLWEwNzctMzVkMC05NDZkLTNkMTY1ZGZlNTQ1Nb7vVN4V2t6t',
    'vu9U3hXa3q0AAAABACpidWlsdGluOm1vbml0b3JlZGVudGl0aWVzLmdlbmVyaWMucmVsYXRpb24ABnRlbmFudAAGdGVuYW50ACQ2OTA5MWE5YS00ODUxLTMyYTItOTg5NS0yNGNhNjNiMmMwMTa-71TeFdrerQ',
    'vu9U3hXa3q0AAAABACxidWlsdGluOmxvZ21vbml0b3JpbmcubG9ncy1vbi1ncmFpbC1hY3RpdmF0ZQAGdGVuYW50AAZ0ZW5hbnQAJDhmYjEzMTczLTRhY2EtM2JkZS05ZDNmLTI0MTM3NWQwZDM0Y77vVN4V2t6t',
    'vu9U3hXa3q0AAAABADpidWlsdGluOnByb2Nlc3MtZ3JvdXAuY2xvdWQtYXBwbGljYXRpb24td29ya2xvYWQtZGV0ZWN0aW9uAAZ0ZW5hbnQABnRlbmFudAAkNGYxYWQxYTEtYTBiNC0zOWE3LTliMmMtMWFjYzBkNTAwMmIzvu9U3hXa3q0',
]


def extract_schema_id_from_object_id(object_id):
    try:
        # Add double equals to force pad regardless of remainder
        # https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding/49459036#49459036
        decoded_object_id_bytes = base64.urlsafe_b64decode(object_id + '==')

        # Remove the first 15 bytes and remove the bytes indicator while converting to a string
        schema_id = str(decoded_object_id_bytes[14:]).replace("b'", "")

        # Truncate after the first byte delimiter that indicates the end of the schema id
        schema_id = schema_id[:schema_id.find('\\')]

        if len(schema_id) < 8 or ':' not in schema_id:
            print('The schema id above may have decode issue!')
            print(warning_statement)

        print(schema_id)
        return schema_id

    except binascii.Error:
        print(f'Decode Failed for {object_id}!')
        print(warning_statement)


def extract_entity_id_from_object_id(object_id):
    try:
        # Add double equals to force pad regardless of remainder
        # https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding/49459036#49459036
        decoded_object_id_bytes = base64.urlsafe_b64decode(object_id + '==')

        # Remove the first 13 bytes and remove the bytes indicator while converting to a string
        entity_id = str(decoded_object_id_bytes[12:]).replace("b'", "")

        # Truncate after the first byte delimiter that indicates the end of the entity id
        entity_id = entity_id[:entity_id.find('\\')]

        if len(entity_id) < 36 or "-" not in entity_id:
            print('The entity id above may have decode issue!')
            print(warning_statement)
        else:
            print(entity_id)
            return entity_id

    except binascii.Error:
        print('Decode Failed!')
        print(warning_statement)


def test():
    for test_object_id in test_object_ids:
        schema_id = extract_schema_id_from_object_id(test_object_id)
        print(f'Object ID: {test_object_id} -> SchemaId: {schema_id}')


def test_update_token():
    for test_update_object_id in test_update_object_ids:
        update_token = get_update_token(test_update_object_id)
        entity_id = extract_entity_id_from_object_id(update_token)
        print(f'Object ID: {test_update_object_id} -> Update Token: {update_token} -> Entity Id: {entity_id}')


def get_update_token(object_id):
    endpoint = '/api/v2/settings/objects'
    settings_object = dynatrace_api.get_by_object_id(env, token, endpoint, object_id)
    update_token = settings_object.get('updateToken')
    print(update_token)
    return update_token


def main():
    print('')
    print(f'Enter an Object ID, "t" to run a test, "tu" to run a test of "updateToken" conversion or "q" to quit')
    print(f'NOTE: to change the environment name from current setting of "{env_name}" requires a code change currently')
    print('')

    while True:
        message = '> '
        object_id = input('%s' % message)

        if object_id.upper() == 'Q':
            print('Exiting per user request')
            exit()

        if object_id.upper() == 'T':
            print('Testing...')
            test()
        else:
            if object_id.upper() == 'TU':
                print('Testing Update Token...')
                test_update_token()
            else:
                extract_schema_id_from_object_id(object_id)


if __name__ == '__main__':
    main()
