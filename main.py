import os
from typing import Optional, List, Dict, Any

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field

from sgr.sgr_library.sgr_device import SGrDevice

app = FastAPI(
    title="SmartGridready Intermediary API",
    description="This API is used to communicate with the SmartGridready Generic Interface.",
    version="1.0.0",
)

instance_counter = 1
interfaces = {}


class InitializationResponse(BaseModel):
    status: str
    instance_id: Optional[str] = None


@app.post("/instances", response_model=InitializationResponse, tags=["instances"],
          summary="Initialize a new instance of the Generic Interface.")
async def initialize(xml: UploadFile = File(...), ini: UploadFile = File(...)):
    global instance_counter, interfaces

    ini_file_ext = os.path.splitext(ini.filename)[-1].lower()
    xml_file_ext = os.path.splitext(xml.filename)[-1].lower()

    print(ini_file_ext)

    if ini_file_ext not in ['.ini'] or xml_file_ext not in ['.xml']:
        raise HTTPException(status_code=400, detail="Incorrect file types uploaded. Expecting .ini and .xml.")

    instance_id = str(instance_counter)

    ini_path = f"{instance_id}.ini"
    xml_path = f"{instance_id}.xml"

    # Async file saving
    with open(ini_path, "wb") as buffer:
        buffer.write(await ini.read())

    with open(xml_path, "wb") as buffer:
        buffer.write(await xml.read())

    if f"{instance_id}" not in interfaces:
        interfaces[f"{instance_id}"] = {}

    interfaces[f"{instance_id}"]["generic_interface"] = SGrDevice()
    interfaces[f"{instance_id}"]["xml"] = xml.filename
    interfaces[f"{instance_id}"]["ini"] = ini.filename

    # Clean up files
    os.remove(ini_path)
    os.remove(xml_path)

    interfaces[f"{instance_id}"]["generic_interface"].update_xml_spec(xml_path).update_config(ini_path).connect()
    await interfaces[f"{instance_id}"]["generic_interface"].connect()

    instance_counter += 1
    return InitializationResponse(status="success", instance_id=instance_id)


# get initialized instances
@app.get("/instances", response_model=Dict[str, Any], tags=["instances"], summary="get initialized instances")
async def get_instances():
    # return only the instance ids, xml and ini paths
    result = {
        key: {
            'instance_id': key,
            'xml': value['xml'],
            'ini': value['ini']
        }
        for key, value in interfaces.items()
    }
    return result


Datapoint = Dict[str, Dict[str, List[str]]]


class ResponseData(BaseModel):
    status: str = Field(..., example="success")
    data: Dict[str, Dict[str, Dict[str, float]]]


@app.post("/get", response_model=ResponseData, tags=["Generic Interface"],
          summary="Get values from the Generic Interface.")
async def get(data: Datapoint):
    """
    ## Retrieve datapoint of specific functional profile 

    ### Request Body

    The request body should be a JSON object where each key represents an identifier and its associated value is another JSON object detailing metrics of interest.

    #### Format:

    ```json
    {
        "<instance_id>": {
            "<fpname>": [
                "<dpname>",
                "<dpname>",
                ...
            ]
        },
        "<instance_id>": {
            "<fpname>": [
                "<dpname>",
                "<dpname>",
                ...
            ]
        },
        ...
    }
    ```

    #### Example:

    ```json
    {
        "1": {
            "ActivePowerAC": ["ActivePowerACtot", "ActivePowerACL1"]
        },
        "2": {
            "ActivePowerAC": ["ActivePowerACtot"]
        }
    }
    ```

    ### Response

    The response format and values will depend on the application's implementation and the data being requested. However, it's expected that the API will return relevant data or status messages based on the identifiers and metrics provided.

    """
    result_dict = {}

    err_string = ""

    for instance_id, fp_data in data.items():
        if instance_id not in result_dict:
            result_dict[instance_id] = {}

        for fpname, dpnames in fp_data.items():
            if fpname not in result_dict[instance_id]:
                result_dict[instance_id][fpname] = {}

            for dpname in dpnames:
                # Your logic to retrieve the value for fpname and dpname
                try:
                    val = await interfaces[instance_id]["generic_interface"].getval(fpname, dpname)
                    result_dict[instance_id][fpname][dpname] = val
                except Exception as e:
                    err_string += f"Error getting value for {fpname}.{dpname}: {e}\n"

    status = err_string if err_string else 'success'
    return {'status': status, 'data': result_dict}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
