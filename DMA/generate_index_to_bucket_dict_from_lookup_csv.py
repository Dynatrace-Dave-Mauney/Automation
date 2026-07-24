import csv


# From Dynatrace Tenant Notebook (load "/lookups/splunk_index_data" Results Download to CSV)
LOOKUP_CSV = '../Lookups/downloads/lookups/splunk_index_data.csv'
SPLUNK_INDEX_COLUMN = 6

# OLD FORMAT, OLD LOCATION
# LOOKUP_CSV = '$splunk_index_data.csv'
# SPLUNK_INDEX_COLUMN = 2

DYNATRACE_BUCKET_COLUMN = 10

index_to_bucket_dict = {}
with open(LOOKUP_CSV, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader, None)  # Skip header row
    for row in reader:
        # print(row)
        splunk_index = row[SPLUNK_INDEX_COLUMN].lower()
        dynatrace_bucket = row[DYNATRACE_BUCKET_COLUMN]
        index_to_bucket_dict[splunk_index] = dynatrace_bucket

print(index_to_bucket_dict)
