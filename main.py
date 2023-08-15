#from sgr.sgr_library.generic_interface import GenericInterface

#import asyncio
from flask import Flask, request, jsonify
from sgr.sgr_library.generic_interface import GenericInterface
from flask_swagger_ui import get_swaggerui_blueprint
from flask import jsonify
import os
app = Flask(__name__)


SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swapper.json'


# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
)

app.register_blueprint(swaggerui_blueprint)
@app.route("/")
def hello_world():
    return "Hello, World!"

interfaces = {}
instance_counter = 1


@app.route("/initialize", methods = ['POST'])
async def initialize():
    """
       Initialisieren der API
       ---
       tags:
         - Initialization
       parameters:
         - name: xml_file
           in: formData
           type: file
           required: true
           description: Die XML-Datei
         - name: ini_file
           in: formData
           type: file
           required: true
           description: Die INI-Datei
       responses:
         200:
           description: Erfolgreiche Initialisierung
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   status:
                     type: string
                   instance_id:
                     type: string
       """
    global interfaces
    global instance_counter
    if request.method == 'POST':
        instance_id = instance_counter
        
        ini_file = ''
        xml_file = ''

        for file in request.files:
            file_obj = request.files[file]
            if file_obj.filename.endswith(('.ini', '.INI')):
                ini_file = f"{instance_id}.ini"
                file_obj.save(ini_file)
            elif file_obj.filename.endswith(('.xml', '.XML')):
                xml_file = f"{instance_id}.xml"
                file_obj.save(xml_file)

        if ini_file and xml_file:
            print('both files provided')
            interfaces[f"{instance_id}"] = GenericInterface(xml_file, ini_file)
            # files wieder löschen
            os.remove(xml_file)
            os.remove(ini_file)
            res = await interfaces[f"{instance_id}"].authenticate()
            print(res)

            response = jsonify({'status': 'success', 'instance_id': f"{instance_id}"})
            response.status_code = 200
            instance_counter = instance_counter + 1
            return response
        else:
            response = jsonify({'status': 'err', 'data': "not all files provided. XML and ini required."})
            response.status_code = 400
            return response

    else:
        # Return an error message if the request method is not POST
        response = jsonify({'error': 'Method not allowed'})
        response.status_code = 405
        return response

@app.route("/get", methods=['POST'])
def get():
    """
    Daten abrufen
    ---
    tags:
      - Data
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: array
            items:
              type: object
              properties:
                instance_id:
                  type: string
                fpname:
                  type: string
                dpname:
                  type: string
    responses:
      200:
        description: Erfolgreiche Datenabfrage
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                data:
                  type: object
    """
    global interfaces
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No JSON received'}), 400

    result_dict = {}

    for endpoint in data:
        instance_id = endpoint.get("instance_id")
        fpname = endpoint.get("fpname")
        dpname = endpoint.get("dpname")
        if instance_id and fpname and dpname:
            interface = interfaces[f'{instance_id}']

            if instance_id not in result_dict:
                result_dict[instance_id] = {}

            if fpname not in result_dict[instance_id]:
                result_dict[instance_id][fpname] = {}

            result_dict[instance_id][fpname][dpname] = interface.getval(fpname, dpname)

    response_data = {
        'status': 'success',
        'data': result_dict
    }

    response = jsonify(response_data)
    response.status_code = 200
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)