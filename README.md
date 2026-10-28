# SGr-Intermediary

## Running the intermediary

### Docker

Note: You may need to install requirements first, as defined in _Local_.

```bash
docker compose up -d
``` 

### Local

1. Clone or check out this repository.

2. Create and activate virtual environment:

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux
source .venv/bin/activate
```

3. Install the requirements:

```bash
pip install -r requirements.txt
```

4. Run the intermediary:

```bash
python main.py
```

> [!NOTE]
> The intermediary will be running on port 8080 either way.

## Running the tests with Postman

1. Import the postman collection from the `Postman` folder.
   2.1 Initialize 2 instances.
   2.2 Now you can read/delete instances and their data.
   2.3 Websockets can't be exported from postman, but here's a screenshot![img.png](img.png).

## API Documentation

The API documentation can be found at `http://localhost:8080/docs` after running the intermediary.

## Disclaimer - Community Support

This project is developed and maintained by the _SmartGridready_ community.
Contributions to the code are encouraged and welcome.
If you would like to contribute bugfixes or features, contact the maintainers.
Please be aware that _SmartGridready_ does not provide commercial support,
and the software is provided "as is" without warranty of any kind.
