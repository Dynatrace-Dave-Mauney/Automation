import json

DMA_REPO_EXTRACT_FILE = '$DMA_Repo_Extract.json'

def main():
    report_lines = []
    with open(DMA_REPO_EXTRACT_FILE, 'r', encoding='utf-8') as infile:
        input_string = infile.read()
        input_json = parse_json_safely(input_string)
        documents = input_json.get('documents')
        for document in documents:
            document_name = document.get('document_name')
            document_type = document.get('document_type')
            document_items = document.get('document_items')
            match = False
            for document_item in document_items:
                bucket = document_item.get('bucket')
                if bucket == 'do not migrate':
                    match = True
            if match:
                report_lines.append((document_name, document_type))

    for report_line in report_lines:
        print(report_line)

    print('')
    print('Total:', len(report_lines))


def parse_json_safely(json_string):
    try:
        data = json.loads(json_string)
        # print("✅ Success! Parsed data:", data)
        return data

    except json.JSONDecodeError as e:
        # Handles malformed JSON strings (e.g., missing quotes, trailing commas)
        print(f"❌ JSON Decode Error: Invalid JSON syntax.")
        print(f"Details: {e.msg} at line {e.lineno}, column {e.colno}")
        return None

    except TypeError as e:
        # Handles incorrect data types passed to loads() (e.g., passing None or an integer)
        print(f"❌ Type Error: Expected a string-like object, but got something else. Details: {e}")
        return None


if __name__ == '__main__':
    main()
