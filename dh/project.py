import json
import os
from jsonschema import validate, ValidationError
from .job import Job
from .pipeline_processors.variables import replace_variables, expand_template

def create_project(data):
    if isinstance(data, dict) and "jobs" in data:
        return Project(data)
    
    # the data object is an array of jobs, so we need to wrap it in a dictionary
    if isinstance(data, list):
        return Project(
            {
                "jobs": data
            }
        )
    
    # the data object is a single job, so we need to wrap it in a list
    return Project(
        {
            "jobs": [data]
        }
    )

class Project:
    def __init__(self, data):
        self.data = data

    def validate(self):
        status, message = validate_data(self.data, load_schema("project"))
        if not status:
            raise Exception(f"Validation error: {message}")

    def run(self, output_dir = "./outputs"):
        expand_template(self.data, self.data.get("template", None))
        replace_variables(self.data["jobs"], self.data.get("variables", None))
        jobs = []

        print(f"Running  project...")
        for item in self.data.get("jobs", []):
            jobs.append(Job(item))

        if len(jobs) == 0:
            raise Exception("No jobs found to run")

        for job in jobs:
            job.run(output_dir)


def validate_data(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True, "Validation successful"
        
    except ValidationError as ve:
        return False, f"Validation error: {ve.message}"
    except json.JSONDecodeError as je:
        return False, f"JSON parsing error: {str(je)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
    

def load_json_file(file_spec):
    with open(file_spec, "r") as file:
        return json.load(file)
    

def load_schema(schema_name):
    return load_json_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{schema_name}_schema.json"))