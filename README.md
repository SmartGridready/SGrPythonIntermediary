# SGr-Intermediary

## Running the intermediary

### Docker

Note: You may need to install requirements first, as defined in _Local_.

```bash
docker compose up --build
``` 

### Local

1. Clone SGrPython repository

Clone the repo manually, alongside `SGrIntermediary`:

```bash
git clone https://github.com/SmartGridready/SGrPython ../SGrPython
```

2. Install the requirements:

```bash
pip install -e ../SGrPython/specification
pip install -e ../SGrPython/commhandler
```

```bash
pip install -r requirements.txt
```

3. Run the intermediary:

```bash
python3 -u main.py
```

> [!NOTE]
> The intermediary will be running on port 5000 either way.

## Running the tests with Postman

1. Import the postman collection from the `Postman` folder.  
   2.1 Initialize 2 instances  
   2.2 Now you can read/delete instances and their data  
   2.3 Websockets can't be exported from postman, but here's a screenshot![img.png](img.png)

## API Documentation

The API documentation can be found at `http://localhost:5000/docs` after running the intermediary.