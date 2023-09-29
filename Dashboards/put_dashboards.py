# Put all dashboards matching the file path pattern to the specified environment.
# Parameters can be passed inline or from command line arguments.

import json
import glob
import os
import sys
import codecs

from Reuse import dynatrace_api
from Reuse import environment


def run():
    """ Used when running directly from an IDE (or from a command line without using command line arguments) """

    # Use the owner stored in properties by default.
    # Override it here or in the put_dashboard call, if needed.
    owner = get_owner()
    # owner = 'nobody@example.com'

    # Default prefix.
    # Override it here or in the put_dashboard call, if needed.
    prefix = ''

    # Put dashboard(s) to the environment name, path, prefix and owner specified.
    # Wildcards like "?" to signify any single character or "*" to signify any number of characters may be used.
    # When wildcards are used, multiple dashboards may be referenced.
    # Example Paths:
    #  Single file reference:
    #   '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json'
    #   '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000117.json'
    #  Multiple file reference (potentially, it depends on the content of the directory):
    #   'Sandbox/00000000-dddd-bbbb-aaaa-????????????.json' # Strict reference
    #   'Sandbox/*.json' # Lenient reference

    # put_dashboards('Prod', '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json', 'Prod', owner)
    # put_dashboards('Prep', '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json', 'Prep', owner)
    # put_dashboards('Dev', '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json', 'Dev', owner)
    # put_dashboards('Personal', '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json', 'Personal', owner)
    # put_dashboards('Demo', '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json', 'Demo', owner)

    # put_dashboards('Personal', 'Sandbox/00000000-dddd-bbbb-aaaa-???????????1.json', 'Personal', owner)

    # owner = get_owner()
    # owner = 'xxxxxx@xxxxxxx.com'
    # put_dashboards('Personal', 'Templates/Overview/00000000-dddd-bbbb-ffff-00000000????.json', 'Personal', owner)
    # put_dashboards('Dev', 'Templates/Overview/00000000-dddd-bbbb-ffff-00000000????.json', 'Dev', owner)
    # put_dashboards('Prep', 'Templates/Overview/00000000-dddd-bbbb-ffff-00000000????.json', 'Prep', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-00000000????.json', 'Prod', owner)

    # owner = 'xxxxx@xxxxxxx.com'
    # put_dashboards('Personal', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000001.json', 'Personal', owner)
    # put_dashboards('Personal', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000807-v1.json', 'Personal', owner)

    # Customer2 Prod (Use None for Prefix when putting from Custom since it has the prefix already set correctly)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000001-v2.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000002.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000003.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000004.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000005.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000006.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000007.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000008.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000009.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000010.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000011.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000012.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000013.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000014-v1.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000017.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000018.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000019.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000020.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000021.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000029.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000030.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000040.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000041.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000042.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000043.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000044.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000045.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000047.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000067.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000068.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000069.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000070.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000071.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000072.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000073.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000074.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000075.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000076.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000077.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000078.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000079.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000080.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000081.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000082.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000083.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000084.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000090.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000091.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000092.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000093.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000094.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000095.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000096.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000100.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000101.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000102.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000103.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000104.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000110.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000111.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000120.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000121.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000800.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000801.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000802.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000803.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000804.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000805.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000806.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000807.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000808.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000809.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000810.json', None, owner)
    # put_dashboards('Prod', 'Custom/Overview-Customer2-Prod/00000000-dddd-bbbb-ffff-000000000900-v1.json', None, owner)

    # Customer2 NonProd (Use None for Prefix when putting from Custom since it has the prefix already set correctly)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000001-v2.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000002.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000003.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000004.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000005.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000006.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000007.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000008.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000009.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000010.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000011.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000012.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000013.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000014-v1.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000017.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000018.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000019.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000020.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000021.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000029.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000030.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000040.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000041.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000042.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000043.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000044.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000045.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000047.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000067.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000068.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000069.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000070.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000071.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000072.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000073.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000074.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000075.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000076.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000077.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000078.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000079.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000080.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000081.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000082.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000083.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000084.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000090.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000091.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000092.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000093.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000094.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000095.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000096.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000100.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000101.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000102.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000103.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000104.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000110.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000111.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000120.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000121.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000800.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000801.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000802.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000803.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000804.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000805.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000806.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000807.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000808.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000809.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000810.json', None, owner)
    # put_dashboards('NonProd', 'Custom/Overview-Customer2-NonProd (With Prod Tags)/00000000-dddd-bbbb-ffff-000000000900-v1.json', None, owner)

    #
    # Development Area Below Here...
    #

    # Database Extensions Work
    # put_dashboards('Prod', 'Curated/Extensions/SQLServer/*SQL Server*.json', 'Prod', owner)
    # put_dashboards('NonProd', 'Curated/Extensions/SQLServer/*SQL Server*.json', 'NonProd', owner)
    # put_dashboards('Prod', '../DynatraceDashboardGenerator/aaaaaaaa-aaaa-aaaa-aaaa-00000000000?.json', 'TEMP', owner)
    # put_dashboards('Prod', '../DynatraceDashboardGenerator/aaaaaaaa-aaaa-aaaa-aaaa-00000000000?.json', 'TEMP', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000077.json', 'Prod', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000085.json', 'Prod', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000086.json', 'Prod', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000087.json', 'Prod', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000088.json', 'Prod', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000089.json', 'Prod', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000090.json', 'Prod', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000097.json', 'Prod', owner)

    # put_dashboards('Prod', '/Users/dave.mauney/PycharmProjects/Automation/$Output/Dashboards/Downloads/TMP/*.json', None, None)
    # put_dashboards('Prod', '../DynatraceDashboardGenerator/aaaaaaaa-aaaa-aaaa-aaaa-00000000000?.json', 'TEMP', owner)
    put_dashboards('Personal', '../NewPlatform/Dashboards/new_platform_dashboard.json', None, owner)


def put_dashboards(env_name, path, prefix, owner):
    print('Prefix: ' + str(prefix))
    print('Owner:  ' + str(owner))
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = f.read()
            dashboard_json = json.loads(dashboard)
            dashboard_id = dashboard_json.get('id')
            dashboard_name = dashboard_json.get('dashboardMetadata').get('name')

            if prefix:
                # Replace well-known placeholder prefixes or add a prefix, as needed
                new_prefix = ''
                if prefix and prefix != '':
                    new_prefix = f'{prefix}: '
                if dashboard_name.startswith('TEMPLATE:'):
                    dashboard_name = dashboard_name.replace('TEMPLATE: ', new_prefix)
                else:
                    if dashboard_name.startswith('BETA:'):
                        dashboard_name = dashboard_name.replace('BETA: ', new_prefix)
                    else:
                        dashboard_name = f'{new_prefix}{dashboard_name}'

                dashboard_json['dashboardMetadata']['name'] = dashboard_name

            if owner:
                dashboard_owner = dashboard_json.get('dashboardMetadata').get('owner')
                dashboard_owner = dashboard_owner.replace('nobody@example.com', owner)
                dashboard_owner = dashboard_owner.replace('Dynatrace', owner)
                dashboard_json['dashboardMetadata']['owner'] = dashboard_owner
            print(filename + ': ' + dashboard_id + ': ' + dashboard_name)

            # Enable "preset" for Dashboard Overview Framework
            if dashboard_id.startswith('00000000-dddd-bbbb-ffff'):
                print(f'Set preset to True for {dashboard_id}:{dashboard_name}')
                dashboard_json['dashboardMetadata']['preset'] = True

            # # Disable "preset" for Dashboard Overview Framework
            # if dashboard_id.startswith('00000000-dddd-bbbb-ffff'):
            #     print(f'Set preset to False for {dashboard_id}:{dashboard_name}')
            #     dashboard_json['dashboardMetadata']['preset'] = False

            # Temp code to modify IDs
            # dashboard_id = dashboard_id.replace('aaaaaaaa-bbbb-cccc-dddd-0', 'aaaaaaaa-bbbb-cccc-dddd-1')
            # dashboard_json['id'] = dashboard_id

            _, env, token = environment.get_environment(env_name)
            tenant = env.split('.')[0].split('/')[2]

            new_tiles = []
            found = False
            tiles = dashboard_json.get('tiles')
            for tile in tiles:
                tile_type = tile.get('tileType')
                if tile_type == 'MARKDOWN':
                    tile_string = str(tile)
                    if '{{.tenant}}' in tile_string:
                        found = True
                        tile_string = tile_string.replace('{{.tenant}}', tenant)
                        new_tiles.append(eval(tile_string))
                    else:
                        new_tiles.append(tile)

            if found:
                dashboard_json['tiles'] = new_tiles

            put_dashboard(env, token, dashboard_id, json.dumps(dashboard_json))

            print(env + '/#dashboard;id=' + dashboard_id)


def get_owner():
    return os.environ.get('DASHBOARD_OWNER_EMAIL', 'nobody@example.com')


def put_dashboard(env, token, dashboard_id, payload):
    endpoint = '/api/config/v1/dashboards'
    dynatrace_api.put(env, token, endpoint, dashboard_id, payload)


def main(arguments):
    usage = '''
    put_dashboards.py: Put dashboards from a file path to the tenant/environment.

    Usage:    put_dashboards.py <tenant/environment URL> <token> <path> <prefix> <owner>
    Examples: put_dashboards.py https://<TENANT>.live.dynatrace.com dt0c01.ABC.DEF /dashboards DEV nobody@example.com 
              put_dashboards.py https://<TENANT>.dynatrace-managed.com/e/<ENV> dt0c01.ABC.DEF /dashboards DEV nobody@example.com
    '''

    print('args' + str(arguments))
    if len(arguments) == 1:
        run()
        exit()
    if len(arguments) < 2:
        print(usage)
        raise ValueError('Too few arguments!')
    if len(arguments) > 4:
        print(help)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help)
    elif arguments[1] in ['-v', '--version']:
        print('1.0')
    else:
        if len(arguments) == 4:
            put_dashboards(arguments[1], arguments[2], arguments[3], arguments[3])
        else:
            print(usage)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
