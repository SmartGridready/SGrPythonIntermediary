# SGr-Intermediary

- download the submodule (after cloning the repo)
``` 
git submodule init
git submodule update
```
- checkout the correct commit of the SGrPytho library
```
cd sgr
git checkout 31d6e3d
```
- replace the `getval` function in sgr/sgr_library/restapi_client_async.py:
```
def getval(self, fp_name, dp_name):
    dp = find_dp(self.root, fp_name, dp_name)
    request_path = dp.rest_apidata_point[0].rest_service_call.request_path
    url = 'https://' + str(self.base_url) + str(request_path)
    query = str(dp.rest_apidata_point[0].rest_service_call.response_query.query)

    headers = {header_entry.header_name: header_entry.value for header_entry in
               dp.rest_apidata_point[0].rest_service_call.request_header.header}
    headers['Authorization'] = 'Bearer ' + self.token

    res = requests.get(url=url, headers=headers)
    print(f"GETVAL: {res.status_code}")
    response = res.json()
    response = json.dumps(response)
    value = jmespath.search(query, json.loads(response))
    return value
```
- build the docker image:
```
docker build -t sgr-intermediary .
```
- run flask app
``` 
Mac:
docker run --rm -p 5000:5000 --name sgr-intermediary -v `pwd`/main.py:/app/main.py -v `pwd`/lehmann.ini:/app/lehmann.ini sgr-intermediary python3 -u main.py

docker run --rm -p 5000:5000 --name sgr-intermediary -v `pwd`/main.py:/app/main.py sgr-intermediary python3 -u main.py


Windows:
docker run --rm -p 5000:5000 --name sgr-intermediary -v ${PWD}/main.py:/app/main.py sgr-intermediary python3 -u main.py
``` 