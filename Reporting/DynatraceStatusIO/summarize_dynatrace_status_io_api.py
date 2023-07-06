#
# Summarize the Dynatrace Status IO API results.
#
# This is an example that is currently configured for a specific customer and can be customized per customer,
# or it can be configured to summarize all statuses.
#

import json
import requests

print_all_statuses = False
print_all_statuses_detailed = False
print_statuses_of_interest = True

status_items_of_interest = ['AWS - Cluster 37 in US West Oregon']


def summarize_status_io_api():
    response = requests.get('https://api.status.io/1.0/status/546d8cb6af8407b6730000cb')

    api_response = json.loads(response.text)

    # print(api_response)

    result = api_response.get('result')
    status_overall = result.get('status_overall')
    overall_status = status_overall.get('status')

    print(f'dynatrace.status.io overall_status is currently "{overall_status}"')

    status_item_list = result.get('status')

    # Full list of statuses
    if print_all_statuses:
        for status_item in status_item_list:
            name = status_item.get('name')
            status = status_item.get('status')
            print(f'{name}: {status}')

    # Full list of statuses with container status details
    if print_all_statuses_detailed:
        for status_item in status_item_list:
            name = status_item.get('name')
            status = status_item.get('status')
            print(f'{name}: {status}')
            containers = status_item.get('containers')
            for container in containers:
                container_name = container.get('name')
                container_status = container.get('status')
                print(f'  {container_name}: {container_status}')

    # Print statuses of interest
    if print_statuses_of_interest:
        for status_item in status_item_list:
            name = status_item.get('name')
            if name in status_items_of_interest:
                status = status_item.get('status')
                print(f'{name}: {status}')
                containers = status_item.get('containers')
                for container in containers:
                    container_name = container.get('name')
                    container_status = container.get('status')
                    print(f'  {container_name}: {container_status}')


    # Report any incidents
    incident_list = result.get('incidents')
    if incident_list:
        print('')
        print('Incidents:')
        incident_count = len(incident_list)
        if incident_count > 1:
            print(f'There are {len(incident_list)} incidents being reported currently')
        else:
            print(f'There is {len(incident_list)} incident being reported currently')

        for incident in incident_list:
            incident_name = incident.get('name')
            incident_open_time = incident.get('datetime_open')
            print(f'"{incident_name}" incident opened {incident_open_time}')
            incident_messages = incident.get('messages')
            if incident_messages:
                print('Incident Details')
                for incident_message in incident_messages:
                    print(incident_message.get('details'))


def main():
    print('Dynatrace Status IO API Summary')
    summarize_status_io_api()


if __name__ == '__main__':
    main()

