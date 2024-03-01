"""
Generate links to each "standard" Multidimensional Analysis View per tenant specified.

For each MDA you want to save, copy the name, click the link and paste the name when you save the MDA.
"""

import os

tenant_keys = ['DYNATRACE_PROD_TENANT', 'DYNATRACE_PREPROD_TENANT', 'DYNATRACE_DEV_TENANT']

mda_url_path = '/ui/diagnostictools/mda'

mda_names_and_params = [
	('Failed Queries', 'metric=FAILED_REQUEST_COUNT&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%110%103%110'),
	('HTTP 4xx Details', 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D%20%7BHTTP-Method%7D%20%7BRequest:Name%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11400-499'),
	('HTTP 4xx Summary', 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11400-499'),
	('HTTP 5xx Details', 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D%20%7BHTTP-Method%7D%20%7BRequest:Name%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11500-599'),
	('HTTP 5xx Summary', 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11500-599'),
	('HTTP 5xx by Exception', 'metric=HTTP_5XX_ERROR_COUNT&dimension=%7BException:Class%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E29%110%140'),
	('HTTP No Response Details', 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D%20%7BHTTP-Method%7D%20%7BRequest:Name%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11-1'),
	('Health Checks', 'metric=REQUEST_COUNT&dimension=%7BRelative-URL%7D%20from%20%7BRequestAttribute:User%20Agent%20Type%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%109%11Health%20Check%20Request%14Health%20Check%20Request'),
	('Key Requests: Failures', 'metric=FAILED_REQUEST_COUNT&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E61%110'),
	('Key Requests: Slowness', 'metric=RESPONSE_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=P90&percentile=80&chart=COLUMN&servicefilter=0%1E61%110%100%116000000%144611686018427387'),
	('Long Lock Times', 'metric=LOCK_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=P90&percentile=80&chart=COLUMN&servicefilter=0%1E20%111%144611686018427387'),
	('Long Wait Times', 'metric=WAIT_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=P90&percentile=80&chart=LINE&servicefilter=0%1E26%112%1026%111%1019%111000%144611686018427387'),
	('Number of DB Calls', 'metric=DATABASE_CHILD_CALL_COUNT&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=AVERAGE&percentile=80&chart=COLUMN&servicefilter=0%1E37%111%144611686018427387'),
	('Slow Queries', 'metric=RESPONSE_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=AVERAGE&percentile=80&chart=COLUMN&servicefilter=0%1E26%110%100%111000000%144611686018427387'),
	('Slow Web Requests', 'metric=RESPONSE_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=AVERAGE&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%100%116000000%144611686018427387'),
	('Slow Web Requests: Percentile', 'metric=RESPONSE_TIME&dimension=%7BRequest:Name%7D%20&mergeServices=false&aggregation=P90&percentile=80&chart=COLUMN&servicefilter=0%1E26%111%1026%112%100%116000000%144611686018427387'),
	('Synthetic 4xx and 5xx Requests', 'metric=REQUEST_COUNT&dimension=%7BHTTP-Method%7D%20%7BURL:Host%7D%7BRelative-URL%7D%20%7BHTTP-Status%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11400-599%1015%11aaaaaaaa-bbbb-cccc-dddd-000000000013%14DynatraceSynthetic'),
	('Tenable Calls', 'metric=REQUEST_COUNT&dimension=%7BHTTP-Method%7D%20%7BRequest:Name%7D%20%7BURL:Host%7D%20%7BRelative-URL%7D%20%7BHTTP-Status%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E15%11aaaaaaaa-bbbb-cccc-dddd-000000000102%14%140%14%14%14%14'),
	('User Agent Type Summary', 'metric=REQUEST_COUNT&dimension=%7BRequestAttribute:User%20Agent%20Type%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E15%11aaaaaaaa-bbbb-cccc-dddd-000000000013'),
]

for tenant_key in tenant_keys:
	tenant = os.environ.get(tenant_key)
	tenant_url = f'https://{tenant}.live.dynatrace.com'
	print('')
	print(tenant_key)
	for mda_name_and_params in mda_names_and_params:
		mda_name = mda_name_and_params[0]
		mda_params = mda_name_and_params[1]
		url = f'{tenant_url}{mda_url_path}?{mda_params}'
		print(f'{mda_name}: {url}')