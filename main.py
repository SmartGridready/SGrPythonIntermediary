#from sgr.sgr_library.generic_interface import GenericInterface

#import asyncio
#from flask import Flask, request, jsonify
from sgr.sgr_library.generic_interface import GenericInterface
#from flask_swagger_ui import get_swaggerui_blueprint
#from flask import jsonify
import asyncio
#app = Flask(__name__)

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from pydantic import BaseModel, Field
import uvicorn
import os
from typing import Optional, List, Dict

app = FastAPI()



SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swapper.json'

# # Call factory function to create our blueprint
# swaggerui_blueprint = get_swaggerui_blueprint(
#     SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
#     API_URL,
#     config={  # Swagger UI config overrides
#         'app_name': "Test application"
#     },
# )

# app.register_blueprint(swaggerui_blueprint)
@app.route("/")
def hello_world():
    return "Hello, World!"

class InitializationResponse(BaseModel):
    status: str
    instance_id: Optional[str] = None

instance_counter = 1  # initialize your instance counter
interfaces = {}  # initialize your interfaces dict

async def authenticate(instance_id: str, xml_file: UploadFile = File(...), ini_file: UploadFile = File(...)) -> InitializationResponse:
    # Your authentication logic here, consider also moving file saving logic here if it's related to authentication
    ...

@app.post("/initialize", response_model=InitializationResponse)
async def initialize(xml: UploadFile = File(...), ini: UploadFile = File(...)):
    global instance_counter, interfaces

    ini_file_ext = os.path.splitext(ini.filename)[-1].lower()
    xml_file_ext = os.path.splitext(xml.filename)[-1].lower()

    print( ini_file_ext)
    
    if ini_file_ext not in ['.ini'] or xml_file_ext not in ['.xml']:
        raise HTTPException(status_code=400, detail="Incorrect file types uploaded. Expecting .ini and .xml.")

    instance_id = str(instance_counter)

    # Assuming you need to save the files, adapt as needed
    ini_path = f"{instance_id}.ini"
    xml_path = f"{instance_id}.xml"

    # Async file saving
    with open(ini_path, "wb") as buffer:
        buffer.write(await ini.read())
    
    with open(xml_path, "wb") as buffer:
        buffer.write(await xml.read())
    
    # Assuming an authenticate method in your interface, that possibly checks the files and initializes something
    # Since FastAPI is async, we can await authenticate directly if it's defined with async def
    
    interfaces[f"{instance_id}"] = GenericInterface(xml_path, ini_path)

    # Clean up files
    os.remove(ini_path)
    os.remove(xml_path)

    await interfaces[f"{instance_id}"].authenticate()

    instance_counter += 1
    return InitializationResponse(status="success", instance_id=instance_id)
    #return response_model



class Datapoint(BaseModel):
    instance_id: str = Field(..., example="1")
    fpname: str = Field(..., example="example_fpname")
    dpname: str = Field(..., example="example_dpname")

class InstanceData(BaseModel):
    instance_id: int = Field(..., example=10)
    fpname: str = Field(..., example="ActivePowerAC")
    dpname: str = Field(..., example="ActivePowerACtot")
    val: float = Field(..., example=12)

class ResponseData(BaseModel):
    status: str = Field(..., example="success")
    data: List[InstanceData]

@app.post("/get", response_model=ResponseData)
async def get(datapoints: List[Datapoint]):
    # prepare response data
    result_dict = []

    for dp in datapoints:
        instance_id = dp.instance_id
        fpname = dp.fpname
        dpname = dp.dpname
        
        # check if all data is provided
        if instance_id and fpname and dpname:

            #result_dict[instance_id][fpname][dpname] = await interfaces[f'{instance_id}'].getval(fpname, dpname)
            result_dict.append({
                "instance_id": instance_id,
                "fpname": fpname,
                "dpname": dpname,
                "val": await interfaces[instance_id].getval(fpname, dpname)
            })

    print(result_dict)

    response_data = {
        'status': 'success',
        'data': result_dict
    }
    return response_data


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)