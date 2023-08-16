#
# Generic selected file copy module.
#
# Currently configured for matching on JSON contents, but can be easily modified to process other file types,
#

import glob
import json
import os
import shutil
from json import JSONDecodeError

INPUT_PATH = '/Temp/builtinoneagent.features_input'
OUTPUT_PATH = '/Temp/builtinoneagent.features_output'

confirmation_required = True
remove_directory_at_startup = True

strings_of_interest = [
    'SENSOR_DOTNET_LOG_ENRICHMENT',
    'DOTNET_LOG_ENRICHMENT_UNSTRUCTURED',
    'SENSOR_DOTNET_BIZEVENTS_HTTP_INCOMING',
    'DOTNET_HTTP_TAGGING_SENSOR_V2',
    'SENSOR_DOTNET_KAFKA',
    'DOTNET_WCF_SENSOR_V2',
    'SENSOR_APACHE_LOG_ENRICHMENT',
    'NODE_JS_AMBIENT_SAMPLING_CAPTURING',
    'ONEAGENT_CROSS_ENV_COORD_SAMPLING',
    'ONEAGENT_CROSS_ENV_RESP_TAGGING',
    'DOTNET_WCF_TAGGING',
    'JAVA_RESOURCE_EXHAUSTED_EVENT_FORWARDING',
    'DOTNET_ASPNETCORE_UEM',
    'FRONTEND_AGENT_IMPROVED_SERVER_BALANCING',
    'GO_LOG_ENRICHMENT',
    'GO_SQL_PGX',
    'GO_CASP_SOFTWARE_COMPONENTS',
    'DOTNET_IN_PROC_TAGGING_V2',
    'SENSOR_JAVA_LOG_ENRICHMENT',
    'JAVA_LOG_ENRICHMENT_UNSTRUCTURED',
    'JAVA_APACHE_HTTP_CLIENT_5',
    'JAVA_KAFKA_STREAMS',
    'JAVA_REACTOR3_CORE_TRACING',
    'JAVA_UEM_INSTRUMENTATION',
    'SENSOR_JAVA_CASP_FLAW_FINDER',
    'JAVA_CASP_CALL_COUNTER',
    'SENSOR_NGINX_LOG_ENRICHMENT',
    'NODEJS_LOG_ENRICHMENT',
    'SENSOR_NODEJS_KAFKAJS',
    'NODEJS_ORACLEDB',
    'NODEJS_WORKERTHREADS',
    'SENSOR_DOTNET_OPENTELEMETRY',
    'SENSOR_GO_OPENTELEMETRY',
    'JAVA_OPENTELEMETRY',
    'NODEJS_OPENTELEMETRY',
    'SENSOR_PHP_OPENTELEMETRY',
    'JAVA_OPENTELEMETRY_JAVA_INSTRUMENTATION_AGENT',
    'JAVA_OPENTRACING_OVERRIDE',
    'JAVA_OPENTRACING',
    'JAVA_OPENTRACING_TRACERRESOLVER_OVERRIDE',
    'SENSOR_PHP_LOG_ENRICHMENT',
    'PHP_AUTOSENSOR_ALL_WORKERS',
    'SENSOR_PHP_PREDIS',
    'SENSOR_PHP_GRPC',
    'JAVA_REACTOR_NETTY_HTTP_CLIENT',
    'JAVA_SPRING_KAFKA',
    'METRICS_ENRICHMENT_NON_INSTRUMENTED_TECH',
    'SENSOR_WEBSERVER_BIZEVENTS_HTTP_INCOMING',
]


def copy_selected_files():
    confirm('Copy selected files from ' + INPUT_PATH + ' to ' + OUTPUT_PATH)
    initialize()

    for filename in glob.glob(INPUT_PATH + '/*'):
        if os.path.isfile(filename):
            process_file(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_directory(path):
    for filename in glob.glob(path + '/*'):
        if os.path.isfile(filename):
            process_file(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_file(filename):
    # print(f'Processing {filename}')

    with open(filename, 'r', encoding='utf-8') as f:
        if filename.endswith('.json'):
            infile_content = f.read()
            try:
                infile_content_json = json.loads(infile_content)
                key = infile_content_json.get('key')
                print(key)
                if key in strings_of_interest:
                    print('match!')
                    output_filename = f'{OUTPUT_PATH}/{os.path.basename(filename)}'
                    with open(output_filename, 'w', encoding='utf-8') as outfile:
                        # To pretty print JSON:
                        # outfile.write(json.dumps(infile_content_json, indent=4, sort_keys=False))
                        # To write file as is
                        outfile.write(infile_content)
            except JSONDecodeError:
                print(f'Skipping due to non-JSON file content: {filename}')
        else:
            print(f'Skipping due to non-JSON file type: {filename}')


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + OUTPUT_PATH + ' directory will now be removed to prepare for the conversion.')
        remove_directory(OUTPUT_PATH)

    if not os.path.isdir(OUTPUT_PATH):
        make_directory(OUTPUT_PATH)


def remove_directory(path):
    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


def make_directory(path):
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def confirm(message):
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            print('Operation aborted')
            exit()


def main():
    copy_selected_files()


if __name__ == '__main__':
    main()
