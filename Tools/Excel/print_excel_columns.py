import openpyxl

# 1. Load the workbook and select the active sheet
wb = openpyxl.load_workbook("$MSHS Server Inventory.xlsx", data_only=True)
sheet = wb.active

# 2. Iterate through rows and print columns B (2) and C (2)
for row in sheet.iter_rows(min_row=1, values_only=True):
    # Convert values to string, handling empty (None) cells gracefully
    val_b = str(row[1]) if row[1] is not None else ""
    val_c = str(row[2]) if row[2] is not None else ""

    print(f"Column B: {val_b} | Column C: {val_c}")