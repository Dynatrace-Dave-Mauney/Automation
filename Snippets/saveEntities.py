"""
Fetch dashboards and store them on disk. 
"""
import requests, ssl, os, sys, json
#My personal SaaS Tenant
#ENV = 'https://********.live.dynatrace.com'
#PATH_PREFIX='/********'
#TOKEN = '*********************'

#Demo Managed Tenant
#ENV = 'https://******.managed-sprint.dynalabs.io/e/*****************************************'
#PATH_PREFIX='/Demo'
#TOKEN = '*********************'

HEADERS = {'Authorization': 'Api-Token ' + TOKEN}

PATH = os.getcwd()

def save(path, file, content):
        if not os.path.isdir(PATH + path): 
                os.makedirs(PATH + path)
        with open(PATH + path + "/" + file, "w", encoding='utf8') as text_file:
                text_file.write("%s" % json.dumps(content, indent=4))

def saveList(list_type):
        try:
                r = requests.get(ENV + '/api/config/v1/' + list_type, headers=HEADERS)
                print("%s save list: %d" % (list_type, r.status_code))
                print(r)
                res = r.json()
                print(res)
                DIRECTORY_PATH=PATH_PREFIX + '/api/config/v1/' + list_type + '/'
                print('Saving to directory path: ' + DIRECTORY_PATH)
                for entry in res['values']:
                        print(entry['id'])
                        tr = requests.get(ENV + '/api/config/v1/' + list_type + '/' + entry['id'], headers=HEADERS)
                        save(DIRECTORY_PATH, entry['id'], tr.json())
        except ssl.SSLError:
                print("SSL Error")

def saveEntity(entity_type):
        try:
                r = requests.get(ENV + '/api/config/v1/' + entity_type, headers=HEADERS)
                #print(r)
                entry = r.json()
                DIRECTORY_PATH=PATH_PREFIX + '/api/config/v1/' + entity_type + '/'
                print('Saving to directory path: ' + DIRECTORY_PATH)
                save(DIRECTORY_PATH, 'entity.json', r.json())
        except ssl.SSLError:
                print("SSL Error")

def saveDashboardList(list_type):
        try:
                r = requests.get(ENV + '/api/config/v1/' + list_type, headers=HEADERS)
                print("%s save list: %d" % (list_type, r.status_code))
                res = r.json()
                DIRECTORY_PATH=PATH_PREFIX + '/api/config/v1/' + list_type + '/'
                print('Saving to directory path: ' + DIRECTORY_PATH)
                for entry in res['dashboards']:
                        #if (entry['name'].startswith('TEMPLATE')):
                        print(entry['id'], entry['name'])
                        tr = requests.get(ENV + '/api/config/v1/' + list_type + '/' + entry['id'], headers=HEADERS)
                        save(DIRECTORY_PATH, entry['id'], tr.json())
        except ssl.SSLError:
                print("SSL Error")

def main():
        """
        saveDashboardList('dashboards')

        saveEntity('anomalyDetection/applications')
        saveEntity('anomalyDetection/aws')
        saveEntity('anomalyDetection/databaseServices')
        saveEntity('anomalyDetection/diskEvents')
        saveEntity('anomalyDetection/hosts')
        saveEntity('anomalyDetection/metricEvents')
        saveEntity('anomalyDetection/services')
        saveEntity('anomalyDetection/vmware')
        saveEntity('applicationDetectionRules')
        ####saveList('aws/credentials')
        ####saveList('virtualization/cloudFoundryCredentials')
        saveEntity('dataPrivacy')
        saveEntity('frequentIssueDetection')
        saveEntity('virtualization/kubernetesConfigurations')
        saveEntity('maintenanceWindows')
        saveEntity('symfiles/ios/supportedversion')
        saveEntity('service/ibmMQTracing/imsEntryQueue')
        """
        """
        saveList('applications/web')
        saveList('autoTags')
        saveList('managementZones')
        saveList('notifications')
        saveList('service/requestAttributes')
        saveList('service/customServices/dotNet')
        saveList('service/customServices/go')
        saveList('service/customServices/java')
        saveList('service/customServices/php')
        """
if __name__ == '__main__':
        main()
