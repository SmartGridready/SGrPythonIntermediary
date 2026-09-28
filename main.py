import asyncio
import os
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocket

from config import load_yaml
from models import ResponseData, InitializationResponse, SetDataPayload, DataPayload
from sgr_commhandler.device_builder import DeviceBuilder


app = FastAPI(
    title="SmartGridready Intermediary API",
    description="This API is used to communicate with the SmartGridready Generic Interface.",
    version="1.0.0",
)

instance_counter = 1
interfaces = {}

# Mount Swagger UI at /docs
app.mount("/docs", StaticFiles(directory="swagger"), name="docs")


async def process_data(data):
    result_dict = {}
    err_string = ""

    for instance_id, fp_data in data.items():
        if instance_id not in result_dict:
            result_dict[instance_id] = {}

        for fpname, dpnames in fp_data.items():
            if fpname not in result_dict[instance_id]:
                result_dict[instance_id][fpname] = {}

            for dpname in dpnames:
                try:
                    fp = interfaces[instance_id]["generic_interface"].get_functional_profile(fpname)
                    data_point = fp.get_data_point(dpname)
                    val = await data_point.get_value_async()
                    result_dict[instance_id][fpname][dpname] = val
                except Exception as e:
                    err_string += f"Error getting value for {fpname}.{dpname}: {e}\n"

    return result_dict, err_string


# Additional endpoint for serving OpenAPI schema
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json():
    return app.openapi()


@app.post("/instances", response_model=InitializationResponse, tags=["instances"],
          summary="Initialize a new instance of the Generic Interface.")
async def initialize(xml: UploadFile = File(...), ini: UploadFile = File(...)):
    global instance_counter, interfaces

    ini_file_ext = os.path.splitext(ini.filename)[-1].lower()
    xml_file_ext = os.path.splitext(xml.filename)[-1].lower()

    if ini_file_ext != '.ini' or xml_file_ext != '.xml':
        raise HTTPException(status_code=400, detail="Incorrect file types uploaded. Expecting .ini and .xml.")

    instance_id = str(instance_counter)

    ini_path = f"{instance_id}.ini"
    xml_path = f"{instance_id}.xml"

    # Saving the INI file
    with open(ini_path, "wb") as buffer:
        buffer.write(await ini.read())

    # Saving the XML file
    with open(xml_path, "wb") as buffer:
        buffer.write(await xml.read())

    if f"{instance_id}" not in interfaces:
        interfaces[f"{instance_id}"] = {}

    # Build device interface (process EID XML and INI file)
    dev_interface = DeviceBuilder().eid_path(xml_path).properties_path(ini_path).build()

    interfaces[f"{instance_id}"]["generic_interface"] = dev_interface
    interfaces[f"{instance_id}"]["xml"] = xml_path
    interfaces[f"{instance_id}"]["ini"] = ini_path

    # Cleanup: Removing temporary files
    os.remove(ini_path)
    os.remove(xml_path)

    await interfaces[f"{instance_id}"]["generic_interface"].connect_async()

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


@app.delete("/instances/{instance_id}", tags=["instances"], summary="Delete an instance of the Generic Interface.")
async def delete_instance(instance_id: str):
    if instance_id not in interfaces:
        raise HTTPException(status_code=404, detail="Instance not found.")

    del interfaces[instance_id]

    return {"status": "success"}


@app.post("/get", response_model=ResponseData, tags=["Generic Interface"],
          summary="Get values from the Generic Interface.")
async def get_values(data: DataPayload):
    result_dict, err_string = await process_data(data)
    status = err_string if err_string else 'success'
    return {'status': status, 'data': result_dict}


@app.post("/set", response_model=ResponseData, tags=["Generic Interface"],
          summary="Set values in the Generic Interface.")
async def set_values(data: SetDataPayload):
    result_dict = {}

    err_string = ""

    for instance_id, fp_data in data.items():
        if instance_id not in result_dict:
            result_dict[instance_id] = {}

        for fpname, dpnames in fp_data.items():
            if fpname not in result_dict[instance_id]:
                result_dict[instance_id][fpname] = {}

            for dpname, value in dpnames.items():
                # Logic to set the value for fpname and dpname
                try:
                    print(f"Setting value for {instance_id}.{fpname}.{dpname}: {value}")
                except Exception as e:
                    err_string += f"Error setting value for {instance_id}.{fpname}.{dpname}: {e}\n"

    status = err_string if err_string else 'success'
    return {'status': status, 'data': result_dict}


@app.websocket("/subscribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        while True:
            # Assume 'get_latest_data()' is a function that fetches the latest data

            result_dict, err_string = await process_data(data)

            # Sending the data to the client
            await websocket.send_json({'status': err_string if err_string else 'success', 'data': result_dict})

            # Wait for 10 seconds before fetching new data
            await asyncio.sleep(10)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()


# entry point when running application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
