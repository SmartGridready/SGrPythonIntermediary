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
- build the docker image
```
 docker build --progress=plain --no-cache -t sgr-intermediary .
```
- run app
``` 
Mac:
docker run --rm -p 5000:5000 --name sgr-intermediary -v `pwd`/main.py:/app/main.py sgr-intermediary python3 -u main.py


Windows:
docker run --rm -p 5000:5000 --name sgr-intermediary -v ${PWD}/main.py:/app/main.py sgr-intermediary python3 -u main.py
``` 