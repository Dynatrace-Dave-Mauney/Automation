import json

from Reuse import environment
from Reuse import report_writer

INPUT_FILE_NAME = '$DMA_Repo_Extract_With_IDs.json'


def process(env, token):
    rows = []

    with open(INPUT_FILE_NAME, 'r', encoding='utf-8') as infile:
        dma_extract_json = json.loads(infile.read())
        # formatted_json = json.dumps(original_json, indent=4, sort_keys=False)

        name = dma_extract_json['name']
        documents = dma_extract_json['documents']
        for document in documents:
            document_id = document['document_id']
            document_name = document['document_name']
            document_type = document['document_type']
            document_items = document['document_items']
            for document_item in document_items:
                document_item_bucket = document_item['bucket']
                document_item_index = document_item['index']
                gen3_env = env.replace('live', 'apps')
                document_url = f'{gen3_env}/ui/apps/dynatrace.{document_type}s/{document_type}/{document_id}'
                row_tuple = (document_name, document_type, document_item_bucket, document_item_index, document_url, document_id)
                if row_tuple not in rows:
                    rows.append(row_tuple)

        report_writer.initialize_text_file(None)
        report_name = 'DMA Repo Summary'
        report_headers = ('Document Name', 'Document Type', 'Bucket Reference', 'Index Reference', 'Document URL', 'Document ID')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=(0, 5))
        report_writer.write_html(None, report_name, report_headers, rows)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    env_name_supplied = 'NonProd'
    # env_name_supplied = 'Int'
    # env_name_supplied = 'Personal'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
