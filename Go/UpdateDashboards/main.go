package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

func main() {
	fmt.Println("func main")

	// Process command line arguments
	dtEnvURL := os.Args[1]
	apiToken := os.Args[2]
	dirname := os.Args[3]

	fmt.Println("URL:                            ", dtEnvURL)
	fmt.Println("Token (1st 15 characters only): ", apiToken[:15])
	fmt.Println("Directory:                      ", dirname)

	f, err := os.Open(dirname)
	if err != nil {
		log.Fatal(err)
	}
	files, err := f.Readdir(-1)
	f.Close()
	if err != nil {
		log.Fatal(err)
	}

	for _, file := range files {
		//fmt.Println(file.Name())
		buf, err := ioutil.ReadFile(dirname + "/" + file.Name())
		dashboard_string := string(buf)
		//fmt.Println(dashboard_string)
		updateDashboard(dtEnvURL, apiToken, dashboard_string, file.Name())
		if err != nil {
			fmt.Println(err)
		}
	}
}

func updateDashboard(dtEnvURL string, token string, dashboard string, id string) {
	//fmt.Println("id: ", id)
	localVarPath := dtEnvURL + "/api/config/v1/dashboards/" + id

	client := &http.Client{}

	req, err := http.NewRequest("PUT", localVarPath, bytes.NewBuffer([]byte(dashboard)))
	req.Header.Add("Content-Type", "application/json; charset=utf-8")
	req.Header.Add("Authorization", "Api-Token "+token)
	if err != nil {
		fmt.Println(err)
	}

	//fmt.Println(req)

	resp, err := client.Do(req)

	if err != nil {
		fmt.Println(err)
		panic(err)
	}
	fmt.Println("id:", id, "Status:", resp.StatusCode)
}
