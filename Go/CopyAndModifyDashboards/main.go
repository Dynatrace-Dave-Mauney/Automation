package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"
)

// {PERF, PROD, DEV}
var replacements = [3][3]string{
	{"6989085264015807372", "-3972168954864528978", "1479185765346578311"},   /*  initializers for row indexed by 0 */
	{"Ecommerce B2C Perf", "Ecommerce B2C Production", "Ecommerce B2C Perf"}, /*  initializers for row indexed by 1 */
	{"https://dynatrace.np.costco.com/e/5c210202-713c-45a3-9d09-e20ca3e19b17", "https://dynatrace.corp.costco.com/e/95c9a5e9-747a-4467-adda-e1cb1b5e31ed", "https://dynatracedev.np.costco.com/e/8f594684-56ac-4e69-af9d-4944180bc6d4"}}

func main() {
	fmt.Println("func main")

	// Process command line arguments
	fromDir := os.Args[1]
	toDir := os.Args[2]
	targetEnv := os.Args[3]

	fmt.Println("From Directory:     ", fromDir)
	fmt.Println("To Directory:       ", toDir)
	fmt.Println("Target Environment: ", targetEnv)

	modifyDashboards(fromDir, toDir, targetEnv)
}

func modifyDashboards(fromDir string, toDir string, targetEnv string) {
	f, err := os.Open(fromDir)
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
		buf, err := ioutil.ReadFile(fromDir + "/" + file.Name())
		dashboard_string := string(buf)
		//fmt.Println(dashboard_string)
		if strings.Contains(dashboard_string, "Migration:") {
			modified_dashboard := modifyDashboard(dashboard_string, targetEnv)
			writeDashboard(toDir, file.Name(), modified_dashboard)
			if err != nil {
				fmt.Println(err)
			}
		}
	}
}

func modifyDashboard(dashboard_string string, targetEnv string) string {
	// DEV is index 2 in "replacements"
	idx := 2
	if targetEnv == "PROD" {
		idx = 1
	} else {
		if targetEnv != "DEV" {
			panic("targetEnv: " + targetEnv + " invalid!")
		}
	}

	var row int

	modString := dashboard_string
	for row = 0; row < 3; row++ {
		modString = strings.ReplaceAll(modString, replacements[row][0], replacements[row][idx])
		fmt.Println(replacements[row][0], "->", replacements[row][idx])
	}
	//fmt.Println(modString)
	return modString
}

func writeDashboard(toDir string, fileName string, dashboard string) {
	err := ioutil.WriteFile(toDir+"/"+fileName, []byte(dashboard), 0644)
	check(err)
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}
