import csv
import openpyxl

from pathlib import Path


# From Dynatrace Tenant Notebook (load "/lookups/splunk_index_data" Results Download to CSV)
LOOKUP_CSV = '$splunk_index_data.csv'

# From DMA Curation Server/Assessment/LOE Assessment Export
DMA_LOE_XLSX = '$LOE_Assessment_dma_splunk_53_com_2026-07-24.xlsx'

index_to_bucket_dict = {}
with open(LOOKUP_CSV, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        splunk_index = row[2].lower()
        dynatrace_bucket = row[10]
        index_to_bucket_dict[splunk_index] = dynatrace_bucket

wb = openpyxl.load_workbook("$LOE_Assessment_dma_splunk_53_com_2026-07-24.xlsx")
ws = wb["Indexes - Buckets"]

for row in range(2, ws.max_row + 1):
    splunk_index = ws[f"B{row}"].value

    dynatrace_bucket_target = index_to_bucket_dict.get(splunk_index.lower())
    if dynatrace_bucket_target:
        dynatrace_bucket_current_value = ws[f"R{row}"].value
        if dynatrace_bucket_current_value != dynatrace_bucket_target:
            print(f'Updating target bucket of index {splunk_index} to {dynatrace_bucket} from {dynatrace_bucket_current_value}')
            ws[f"R{row}"].value = dynatrace_bucket_target

OUTFILE_NAME = Path(DMA_LOE_XLSX).stem + '_MODIFIED.xlsx'
wb.save(OUTFILE_NAME)
