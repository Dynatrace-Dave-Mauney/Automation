package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

// Use for all entities: values, credentials, dashboards, extensions
type entityStruct struct {
	Id   string
	Name string
}

type entitiesStruct struct {
	Values []entityStruct
}

var CONFIG_API_ENDPOINT_PREFIX = "api/config/v1"

// Process command line arguments
var dtEnvURL = os.Args[1]
var apiToken = os.Args[2]
var subdir = os.Args[3]

var saveEntityEndpoints = []string{
	"/allowedBeaconOriginsForCors",
	"/anomalyDetection/applications",
	"/anomalyDetection/aws",
	"/anomalyDetection/databaseServices",
	"/anomalyDetection/hosts",
	"/anomalyDetection/services",
	"/anomalyDetection/vmware",
	"/applicationDetectionRules/hostDetection",
	"/applications/web/default",
	"/applications/web/default/dataPrivacy",
	"/aws/iamExternalId",
	"/aws/privateLink",
	"/aws/privateLink/allowlistedAccounts",
	"/contentResources",
	"/frequentIssueDetection",
	"/geographicRegions/ipAddressMappings",
	"/geographicRegions/ipDetectionHeaders",
	"/hosts/autoupdate",
	"/symfiles/dtxdss-download",
	"/symfiles/info",
	"/symfiles/ios/supportedversion",
	"/technologies"}

var saveListEndpoints = []string{
	"/alertingProfiles",
	"/anomalyDetection/diskEvents",
	"/anomalyDetection/metricEvents",
	"/applicationDetectionRules",
	"/applications/mobile",
	"/applications/web",
	"/applications/web/dataPrivacy",
	"/autoTags",
	"/aws/credentials",
	"/azure/credentials",
	"/calculatedMetrics/log",
	"/calculatedMetrics/mobile",
	"/calculatedMetrics/rum",
	"/calculatedMetrics/service",
	"/calculatedMetrics/synthetic",
	"/credentials",
	"/cloudFoundry/credentials",
	"/dashboards",
	"/dataPrivacy",
	"/extensions",
	"/extensions/activeGateExtensionModules",
	"/kubernetes/credentials",
	"/maintenanceWindows",
	"/managementZones",
	"/notifications",
	"/plugins",
	"/plugins/activeGatePluginModules",
	"/remoteEnvironments",
	"/reports",
	"/service/detectionRules/FULL_WEB_REQUEST",
	"/service/detectionRules/FULL_WEB_SERVICE",
	"/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST",
	"/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE",
	"/service/failureDetection/parameterSelection/parameterSets",
	"/service/failureDetection/parameterSelection/rules",
	"/service/ibmMQTracing/imsEntryQueue",
	"/service/ibmMQTracing/queueManager",
	"/service/requestAttributes",
	"/service/requestNaming",
	"/service/resourceNaming",
	"/symfiles"}

func main() {
	fmt.Println("func main")

	fmt.Println("URL:                            ", dtEnvURL)
	fmt.Println("Token (1st 15 characters only): ", apiToken[:15])
	fmt.Println("Subdirectory:                   ", subdir)

	fmt.Println("Args Length:                    ", len(os.Args))

	if len(os.Args) == 6 {
		mode := os.Args[4]
		endpoints := os.Args[5]
		if mode == "include" {
			endpointList := strings.Split(endpoints, ",")
			for _, endpoint := range endpointList {
				if contains(saveEntityEndpoints, endpoint) {
					fmt.Println("including: ", endpoint)
					saveEntity(endpoint)
				} else {
					if contains(saveListEndpoints, endpoint) {
						fmt.Println("including: ", endpoint)
						saveList(endpoint)
					} else {
						fmt.Println("invalid endpoint: " + endpoint)
						os.Exit(1)
					}
				}
			}
		} else if mode == "exclude" {
			endpointList := strings.Split(endpoints, ",")
			for _, endpoint := range saveEntityEndpoints {
				if contains(endpointList, endpoint) {
					fmt.Println("excluding: ", endpoint)
				} else {
					saveEntity(endpoint)
				}
			}
			for _, endpoint := range saveListEndpoints {
				if contains(endpointList, endpoint) {
					fmt.Println("excluding: ", endpoint)
				} else {
					saveList(endpoint)
				}
			}
		}
		os.Exit(0)
	}

	//Generated with C:\Users\Dave.Mauney\PycharmProjects\Automation\DynatraceAPI\APISpecs\dump_spec.py
	saveEntity("/allowedBeaconOriginsForCors")
	saveEntity("/anomalyDetection/applications")
	saveEntity("/anomalyDetection/aws")
	saveEntity("/anomalyDetection/databaseServices")
	saveEntity("/anomalyDetection/hosts")
	saveEntity("/anomalyDetection/services")
	saveEntity("/anomalyDetection/vmware")
	saveEntity("/applicationDetectionRules/hostDetection")
	saveEntity("/applications/web/default")
	saveEntity("/applications/web/default/dataPrivacy")
	saveEntity("/aws/iamExternalId")
	saveEntity("/aws/privateLink")
	saveEntity("/aws/privateLink/allowlistedAccounts")
	saveEntity("/contentResources")
	saveEntity("/frequentIssueDetection")
	saveEntity("/geographicRegions/ipAddressMappings")
	saveEntity("/geographicRegions/ipDetectionHeaders")
	saveEntity("/hosts/autoupdate")
	saveEntity("/symfiles/dtxdss-download")
	saveEntity("/symfiles/info")
	saveEntity("/symfiles/ios/supportedversion")
	saveEntity("/technologies")
	saveList("/alertingProfiles")
	saveList("/anomalyDetection/diskEvents")
	saveList("/anomalyDetection/metricEvents")
	saveList("/applicationDetectionRules")
	saveList("/applications/mobile")
	saveList("/applications/web")
	saveList("/applications/web/dataPrivacy")
	saveList("/autoTags")
	saveList("/aws/credentials")
	saveList("/azure/credentials")
	saveList("/calculatedMetrics/log")
	saveList("/calculatedMetrics/mobile")
	saveList("/calculatedMetrics/rum")
	saveList("/calculatedMetrics/service")
	saveList("/calculatedMetrics/synthetic")
	saveList("/credentials")
	saveList("/cloudFoundry/credentials")
	saveList("/dashboards")
	saveList("/dataPrivacy")
	saveList("/extensions")
	saveList("/extensions/activeGateExtensionModules")
	saveList("/kubernetes/credentials")
	saveList("/maintenanceWindows")
	saveList("/managementZones")
	saveList("/notifications")
	saveList("/plugins")
	saveList("/plugins/activeGatePluginModules")
	saveList("/remoteEnvironments")
	saveList("/reports")
	saveList("/service/detectionRules/FULL_WEB_REQUEST")
	saveList("/service/detectionRules/FULL_WEB_SERVICE")
	saveList("/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST")
	saveList("/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE")
	saveList("/service/failureDetection/parameterSelection/parameterSets")
	saveList("/service/failureDetection/parameterSelection/rules")
	saveList("/service/ibmMQTracing/imsEntryQueue")
	saveList("/service/ibmMQTracing/queueManager")
	saveList("/service/requestAttributes")
	saveList("/service/requestNaming")
	saveList("/service/resourceNaming")
	saveList("/symfiles")
}

func saveList(entityType string) {
	fmt.Println("func saveList")
	entity := callDynatraceAPI(entityType)
	// fmt.Println(entity)
	if !strings.Contains(entity, "\"error\": {") {
		writeList(entityType, entity)
	} else {
		fmt.Println("payload contains \"error\": {")
		fmt.Println(entityType)
		fmt.Println(entity)
		// os.Exit(0)
	}
}

func saveEntity(entityType string) {
	fmt.Println("func saveEntity")
	entity := callDynatraceAPI(entityType)
	if !strings.Contains(entity, "error") {
		writeEntity(subdir+"/"+CONFIG_API_ENDPOINT_PREFIX+entityType, "entity.json", entity)
	} else {
		fmt.Println("payload contains 'error'")
		fmt.Println(entityType)
		fmt.Println(entity)
		// os.Exit(0)
	}
}

func writeList(entityType string, entity string) {
	writeEntity(subdir+"/"+CONFIG_API_ENDPOINT_PREFIX+entityType, "$list.json", entity)
	fmt.Println("func writeList")
	// fmt.Println(entityType)
	// fmt.Println(entity)
	if entity != "[]" {
		entityToParse := entity
		if entityType == "/credentials" {
			entityToParse = strings.Replace(entityToParse, "credentials", "values", 1)
		}
		if entityType == "/dashboards" {
			entityToParse = strings.Replace(entityToParse, "dashboards", "values", 1)
		}
		if entityType == "/extensions" {
			entityToParse = strings.Replace(entityToParse, "extensions", "values", 1)
		}
		if entityType == "/applications/web/dataPrivacy" {
			entityToParse = strings.Replace(entityToParse, "identifier", "id", -1)
		}
		// fmt.Printf("entityToParse: %v\n", entityToParse)
		var entities entitiesStruct
		err := json.Unmarshal([]byte(entityToParse), &entities)
		if err != nil {
			fmt.Println("error:", err)
			os.Exit(1)
		}
		for k := range entities.Values {
			id := entities.Values[k].Id
			fmt.Printf("id: %v\n", id)
			// If the id is "bad" for urls, or it's an out of the box extension, just skip it!
			if !strings.Contains(id, "%") && !strings.Contains(id, "dynatrace.") && !strings.Contains(id, "ruxit.") {
				endpoint := entityType + "/" + id
				if entityType == "/applications/web/dataPrivacy" {
					endpoint = "/applications/web/" + id + "/dataPrivacy"
				}
				entity := callDynatraceAPI(endpoint)
				// Fix calculated service metric ids
				id = strings.Replace(id, "calc:", "calc-", 1)
				writeEntity(subdir+"/"+CONFIG_API_ENDPOINT_PREFIX+entityType, id, entity)
			}
		}
	}
}

func writeEntity(subdir string, id string, entity string) {
	fmt.Println("func writeEntity")
	fmt.Printf("Sub Directory: %v\n", subdir)
	fmt.Printf("Entity ID:     %v\n", id)
	// fmt.Printf("Entity:\n      %v\n", entity)

	makedir(subdir)
	fname := subdir + "/" + id

	f, err := os.Create(fname)
	check(err)
	defer f.Close()

	w := bufio.NewWriter(f)
	_, err2 := w.WriteString(entity)
	check(err2)
	w.Flush()
}

//Use entityType for lists
//Use entityType + id for individual calls
func callDynatraceAPI(entityType string) (response string) {
	fmt.Println("func callDynatraceAPI")
	// fmt.Printf("entityType: %v\n", entityType)
	url := dtEnvURL + "/" + CONFIG_API_ENDPOINT_PREFIX + entityType
	// fmt.Printf("url: %v\n", url)

	client := &http.Client{}

	req, err := http.NewRequest("GET", url, nil)
	req.Header.Add("Content-Type", "application/json; charset=utf-8")
	req.Header.Add("Authorization", "Api-Token "+apiToken)
	if err != nil {
		fmt.Println(err)
	}

	// fmt.Println(req)

	resp, err := client.Do(req)

	if err != nil {
		fmt.Println(err)
		//panic(err)
	}

	defer resp.Body.Close()
	body, err2 := io.ReadAll(resp.Body)

	if err2 != nil {
		fmt.Println(err2)
		//panic(err2)
	}

	// fmt.Println(string(body))

	var out bytes.Buffer
	err3 := json.Indent(&out, body, "", "    ")

	if err3 != nil {
		fmt.Println(err3)
		//panic(err3)
	}

	response = out.String()

	// fmt.Println(response)

	return response
}

func makedir(subdir string) {
	//fmt.Println("func makedir")
	_, err := os.Stat(subdir)

	if os.IsNotExist(err) {
		errDir := os.MkdirAll(subdir, 0755)
		if errDir != nil {
			fmt.Println(err)
		}
	}
}

func check(e error) {
	if e != nil {
		fmt.Println(e)
		panic(e)
	}
}

// https://play.golang.org/p/Qg_uv_inCek
// contains checks if a string is present in a slice
func contains(s []string, str string) bool {
	for _, v := range s {
		if v == str {
			return true
		}
	}

	return false
}
