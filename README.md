# MVPY
## Context
`mvpy` is a small tool we spread across our local machines and use it to communicate via HTTP REST, it enable us to send commands, or get new information regarding each machines.

## Your Task
### Create a CI/CD pipeline to build and test `mvpy`.

Prerequisites:
 - Clone from this repo to your local machine, using provided deploy private key, see [how to use deploy Keys](https://docs.github.com/en/developers/overview/managing-deploy-keys#using-multiple-repositories-on-one-server).
 - Upload your work to any git provider (prefer GitHub).
 - Write a CI/CD action.

CI/CD Pipeline:
 - Prepare the test files (download if necessary).
 - Create and activate venv
 - Install dependencies
 - Test the code with `pytest` (test files are included)
 - Build with `pyinstaller`
 - Release a version with executables.

## Output:  
We expect: 
 - A link to a public git repo
 - A pipeline file (for GitHub YAML action file)
 - Executables
 and green badge :green_heart:  
 
 **BONUS**: Report file including: building times, code coverage, pytest outpout.  
 **IMPORTANT NOTE**: Please write down the workflow or any problems you encounter and add it to your repo.

##
## Summary
mvpy is mantis vision python binding for MVGRAPH cpp API.

Goal is to have a simple API that we/customers can use for interacting with MVGraphAPI functionality,  
without requiring a large tree of headers and dependencies, allowing interaction from scripting languages.

Current implementation is a CPP singleton that is exposed via C style symbols.  
These symbols are imported into Python using the ctypes library, which can be accessed via HTTP REST methods.  

## Usage
The executable can be run with or without these options:  
| Option | Description |
| --- | --- |
| `--mempool` | Overwrite default library path file (default: 1000). |
| `--lib`,`-l` | Overwrite default library path file (default: current working directory). |
| `--port`,`-p` | Overwrite default port number (default: 7500). |
| `--graph`,`-g` | Graph file to load, either in XML, JSON or TXT format. |
| [[nargs]](https://docs.python.org/3/library/argparse.html#nargs) | Each additional argument will be pass as a cli_param to be injected later to graph (example: NUM=1 PORT=5555). |
<details>
<summary>Examples</summary>

<p>

Basic
```powershell
$ python mvpy_rest_server.py
```

</p>
  
More complex
  
<p>

```powershell
$ python mvpy_rest_server.py --lib C:\ring_it\builds\v1109
```

```powershell
$ python mvpy_rest_server.py --lib . --port 8888 --mempool 1200 --graph C:\RingTeam\graphs\devices_preview.xml NUM=1 PORT=5555 LORDIP=192.168.41.254
```

</p>
</details>  

## MVPY REST API

   * [Get Server status](#get-server-status)
   * [Upload graph](#upload-graph)
   * [Remote graph](#remote-graph)
   * [Build Graph](#build-graph)
   * [Run Graph](#run-graph)
   * [Stop Graph](#stop-graph)
   * [Terminate Graph](#terminate-graph)
   * [Get Graph State](#get-graph-state)
   * [Get Graph Filters](#get-graph-filters)
   * [Get](#get-filter-parameter)/[Set](#set-filter-parameter) Filter Params
   * [Get](#get-cli-params)/[Set](#set-cli-params) CLI Params
   * [Get](#get-graph-playmode)/[Set](#set-graph-playmode) Graph PlayMode
   * [Get](#get-filter-parameters)/[Set](#set-filter-parameters) Multiple Parameters
   

## Get Server status 
Return status 200 (OK) if server is up and running.
### Request

`/server_status [GET]`

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /server_status
Content-Length: 5
"OK"
```   
## Upload graph
Upload a graph file to server (allowed extensions: xml, txt, json).  
Graph file and cli_params must be included in form-data content type. either as raw string, or attached as a file.  
`upload` and `upload_run` are using the same request format. 
### Request

`/graph/upload [POST]` or `/graph/upload_run [POST] `

<details>
<summary>Examples</summary>

<p>

Powershell
```powershell
$Uri = "http://<hostname>:<port>/graph/upload_run"
$filepath = "path/to/file.xml"
$filename = Split-Path $filepath -leaf #=> "file.json"

$FileContent = [IO.File]::ReadAllText($filepath);
$form = @{'PORT'='5555';'filename'=$filename;'file'=$FileContent};
Invoke-RestMethod -Uri $Uri -ContentType 'multipart/form-data' -Method Post -Form $form;
```

</p>
  
Python
  
<p>

```python
import requests
from pathlib import Path

url = "http://<hostname>:<port>/graph/upload_run"
filepath = r"path\to\file.json"
filename = Path(filepath).name #=> "file.json"

files = {'file': open(filepath,'rb')}
cli_params = {'LORDIP': '192.168.42.254', 'PORT': '5555', 'filename': filename}

r = requests.post(url, files=files, data=cli_params)
```

</p>
</details>  

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/upload_run
Content-Length: 16

"Graph uploded"
```

## Remote graph
Build/Build & run remote graph file, Returning list of current graph build filters in JSON.    
Graph file path and cli_params must be included in json content type.  
`build_remote` and `build_remote_run` are using the same request format. 
### Request

`/graph/build_remote [POST]` or `/graph/build_remote_run [POST] `

<details>
<summary>Examples</summary>

<p>

Powershell
```powershell
$Uri = "http://<hostname>:<port>/graph/build_remote_run"
$filepath = "path/to/file.xml"

$JSON = '{"remote_graph": "' + $filepath + '", "cli_params": {"NUC":"1", "PORT":"5556"}}'
Invoke-RestMethod -Uri $Uri -ContentType 'application/json' -Method Post -Body $JSON;
```

</p>
  
Python
  
<p>

```python
import requests
from pathlib import Path

url = "http://<hostname>:<port>/graph/build_remote_run"
filepath = r"path\to\file.json"

cli_params = {"remote_graph": filepath, "cli_params": {"NUC":"1", "PORT":"5556"}}

r = requests.post(url, json=cli_params)
```

</p>
</details>  

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/build_remote_run
Content-Length: 53

{"devices": 0, "vocam": 1, "decoder": 2, "camParamsIR": 3}
```

## Build Graph  
Build the current graph, returning list of current graph build filters in JSON.
### Request

`/graph/build [POST]` `/graph/build_run [POST]`

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/run
Content-Length: 58
{"devices": 0, "vocam": 1, "decoder": 2, "camParamsIR": 3}
```
## Run Graph  
Start running the current graph
### Request

`/graph/run [POST]`

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/run
Content-Length: 23
"Graph is now running" 
```
## Stop Graph  
Stop the current graph
### Request

`/graph/stop [POST]`

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/stop
Content-Length: 16
"Graph stopped" 
```
## Terminate Graph  
Terminate and delete the current graph
### Request

`/graph/terminate [POST]`

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/terminate
Content-Length: 23
"Graph terminated" 
```  
## Get Graph State 
Return the state of current graph
### Request

`/graph/get_state [GET]`

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/get_state
Content-Length: *
| "NOT_BUILT" | "ERROR" | "PLAYING" | "PAUSED" | "STOPPED" 
```

## Get Graph Filters 
Return attached filters of current graph.
Graph must be build before `get_filters` invokation.
### Request

`/graph/get_filters [GET]`

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/get_filters
Content-Length: 58
{"devices": 0, "vocam": 1, "decoder": 2, "camParamsIR": 3}
```

## Get CLI PARAMS 
Return CLI parameters to be injected to the current graph.
### Request

`/get_cli_params [GET]`

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /get_cli_params
Content-Length: *
{"NUC":"1", "LORDIP":"192.168.41.254", "PORT":"5556"}
```
## Set CLI PARAMS 
Set the CLI parameters to be injected to the current graph.

### Request

`/set_cli_params [POST]`

<details>
<summary>Examples</summary>

<p>

Powershell
```powershell
$JSON = '{"cli_params": {"NUC":"1", "LORDIP":"192.168.41.254", "PORT":"5556"}}'
$Uri = "http://<hostname>:<port>/set_cli_params"
Invoke-RestMethod -Uri $Uri -Method Post -Body $JSON -ContentType "application/json"
```

</p>
  
Python
  
<p>

```python
import requests

url = "http://<hostname>:<port>/graph/upload_run"
r = requests.post(url, json={"cli_params": {"NUC":"1", "LORDIP":"192.168.41.254", "PORT":"5556"}})
```

</p>
</details> 

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /set_cli_params
Content-Length: 52
{"NUC":"1", "LORDIP":"192.168.41.254", "PORT":"5556"}
``` 
  
## Get Graph PlayMode 
Return current graph PlayMode
| PlayMode | Description |
| --- | --- |
| `"0"` | `RPM_FORWARD_ONCE` |
| `"1"` | `RPM_FORWARD_LOOP` |
| `"2"` | `RPM_BACKWARD_ONCE` |
| `"3"` | `RPM_BACKWARD_LOOP` |
| `"4"` | `RPM_PINGPONG` |
| `"5"` | `RPM_PINGPONG_INVERSE` |
| `"255"` | `RPM_REALTIME` |
  
### Request

`/graph/get_play_mode [GET]`

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/get_play_mode
Content-Length: *
| "0" | "1" | "2" | "3" | "4" | "5" | "255" 
```
## Set Graph PlayMode  
Set the current graph PlayMode. 
### Request

`/graph/set_play_mode [POST]`
 
<details>
<summary>Examples</summary>

<p>

Powershell
```powershell
$JSON = '{"play_mode": "255"}'
$Uri = "http://<hostname>:<port>/graph/set_play_mode"
Invoke-RestMethod -Uri $Uri -Method Post -Body $JSON -ContentType "application/json"
```

</p>
  
Python
  
<p>

```python
import requests

url = "http://<hostname>:<port>/graph/set_play_mode"
r = requests.post(url, json={"play_mode": "255"})
```

</p>
</details> 
  
### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/set_play_mode
Content-Length: *
{"play_mode": "255"}
```
## Get Filter Parameter 
Return a specific parameter from given filter of current graph.
  
### Request

`/graph/get_filter_param [GET]`
<details>
<summary>Examples</summary>

<p>

Powershell
```powershell
$JSON = '{"unique_name": "fpsanalyzer_1","param_name": "Label"}'
$Uri = "http://<hostname>:<port>/graph/get_filter_param"
Invoke-RestMethod -Uri $Uri -Method Get -Body $JSON -ContentType "application/json"
```

</p>
  
Python
  
<p>

```python
import requests

url = "http://<hostname>:<port>/graph/get_filter_param"
r = requests.post(url, json={"unique_name": "fpsanalyzer_1","param_name": "Label")
```

</p>
</details> 

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/get_filter_param
Content-Length: *
<STRING> 
```
## Set Filter Parameter
Set a specific parameter from given filter of current graph.
### Request

`/graph/set_filter_param [POST]`
<details>
<summary>Examples</summary>

<p>

Powershell
```powershell
$JSON = '{"unique_name": "fpsanalyzer_1","param_name": "Label","param_value": "testF"}'
$Uri = "http://<hostname>:<port>/graph/set_filter_parame"
Invoke-RestMethod -Uri $Uri -Method Post -Body $JSON -ContentType "application/json"
```

</p>
  
Python
  
<p>

```python
import requests

url = "http://<hostname>:<port>/graph/set_filter_param"
r = requests.post(url, json={"unique_name": "fpsanalyzer_1","param_name": "Label","param_value": "testF"})
```

</p>
</details> 
  
### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/set_filter_param
Content-Length: *
{"unique_name": "fpsanalyzer_1","param_name": "Label","param_value": "testF"}
```

## Get Filter Parameters
Return all parameters from given filter of the current graph.
  
### Request

`/graph/get_params [GET]`
<details>
<summary>Examples</summary>

<p>

Powershell
```powershell
$JSON = '{"unique_name": "fpsanalyzer_1"}'
$Uri = "http://<hostname>:<port>/graph/get_params"
Invoke-RestMethod -Uri $Uri -Method Post -Body $JSON -ContentType "application/json"
```

</p>
  
Python
  
<p>

```python
import requests

url = "http://<hostname>:<port>/graph/get_params"
r = requests.post(url, json={"unique_name": "fpsanalyzer_1")
```

</p>
</details> 

### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/get_params
Content-Length: 92
{"PARAMS": ["Enabled": "True","Fps": "0.000000","Label": "CCMpng"],"FilterInstanceID": "4"}
```
## Set Filter Parameters
Set mutliple filters parameters, using a file.
### Request

`/graph/set_params [POST]`

<details>
<summary>Examples</summary>

<p>

Powershell
```powershell
$Uri = "http://<hostname>:<port>/graph/set_params"
$filepath = "path/to/file.xml"
$filename = Split-Path $filepath -leaf #=> "file.json"

$FileContent = [IO.File]::ReadAllText($filepath);
$form = @{'PORT'='5555';'filename'=$filename;'file'=$FileContent};
Invoke-RestMethod -Uri $Uri -ContentType 'multipart/form-data' -Method Post -Form $form;
```

</p>
  
Python
  
<p>

```python
import requests
from pathlib import Path

url = "http://<hostname>:<port>/graph/set_params"
filepath = r"path\to\file.json"
filename = Path(filepath).name #=> "file.json"

files = {'file': open(filepath,'rb')}
cli_params = {'LORDIP': '192.168.42.254', 'PORT': '5555', 'filename': filename}

r = requests.post(url, files=files, data=cli_params)
```

</p>
</details>  
  
### Response

```HTTP
HTTP/1.1 200 OK
Date: Thu, 23 Dec 2021 11:45:15 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Location: /graph/set_params
Content-Length: 26
"Set params successfully"
```
