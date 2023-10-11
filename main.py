from sgr.sgr_library.generic_interface import GenericInterface
import asyncio
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

instance_counter = 1 
interfaces = {} 


@app.post("/initialize", response_model=InitializationResponse)
async def initialize(xml: UploadFile = File(...), ini: UploadFile = File(...)):
    global instance_counter, interfaces

    ini_file_ext = os.path.splitext(ini.filename)[-1].lower()
    xml_file_ext = os.path.splitext(xml.filename)[-1].lower()

    print( ini_file_ext)
    
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
    
    interfaces[f"{instance_id}"] = GenericInterface(xml_path, ini_path)

    # Clean up files
    os.remove(ini_path)
    os.remove(xml_path)

    await interfaces[f"{instance_id}"].authenticate()

    instance_counter += 1
    return InitializationResponse(status="success", instance_id=instance_id)



Datapoint = Dict[str, Dict[str, List[str]]]

class ResponseData(BaseModel):
    status: str = Field(..., example="success")
    data: Dict[str, Dict[str, Dict[str, float]]]

@app.post("/get", response_model=ResponseData)
async def get(data: Datapoint):
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
                  val = await interfaces[instance_id].getval(fpname, dpname)
                  result_dict[instance_id][fpname][dpname] = val
                except Exception as e:
                  err_string += f"Error getting value for {fpname}.{dpname}: {e}\n"

    status = err_string if err_string else 'success'
    return {'status': status, 'data': result_dict}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)