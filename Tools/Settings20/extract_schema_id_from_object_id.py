"""
NOTE:
    This module uses a non-public technique to extract the schema id from an object id.

    This technique is subject to failure at some point due to any change with the underlying encoding.
"""

import base64
import binascii

caveat_emptor = '''This module uses a non-public technique to extract the schema id from an object id.
This technique is subject to failure at some point due to any change with the underlying encoding.
'''

object_ids = [
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

        # Remove the first 13 bytes and remove the bytes indicator while converting to a string
        schema_id = str(decoded_object_id_bytes[14:]).replace("b'", "")

        # Truncate after the first byte delimiter that indicates the end of the schema id
        schema_id = schema_id[:schema_id.find('\\')]

        print(schema_id)

        if len(schema_id) < 8 or ":" not in schema_id:
            print('The schema id above may have a decode issue!')
            print(caveat_emptor)

    except binascii.Error:
        print('Decode Failed!')
        print(caveat_emptor)


def test():
    for object_id in object_ids:
        extract_schema_id_from_object_id(object_id)

if __name__ == '__main__':
    print('')
    print(f'Enter an Object ID, "t" to run a test, or "q" to quit')
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
            exit()

        extract_schema_id_from_object_id(object_id)



