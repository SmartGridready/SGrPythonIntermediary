# SGr-Intermediary

## Getting Started

First change directory to sgr

```
cd sgr
```

Download the submodule (after cloning the repo):

``` 
git submodule init
git submodule update
```

or clone the repo manually:

```
git clone https://github.com/SmartGridready/SGrPython .
```

## Running the intermediary

### Docker:

``` 
sudo docker compose up --build
``` 

### Local:

1. Install the requirements:

```
pip install -r sgr/requirements.txt
```

```angular2html
pip install -r requirements.txt
```

```bash
pip install -e sgr
```

2. Run the intermediary:

```
python3 -u main.py
```

> [!NOTE]
> The intermediary will be running on port 5000 either way.

## API Documentation

The API documentation can be found at `http://localhost:5000/docs` after running the intermediary.