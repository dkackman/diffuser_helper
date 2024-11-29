import os
import json
import torch
import copy
from .pipeline_processors.arguments import realize_args
from .step import Step


class Job:
    def __init__(self, data):
        self.data = data

    def run(self, output_dir):
        try:
            job_id = self.data["id"]
            print(f"Processing {job_id}")

            # prepare the job by realizing the arguments
            # ie fetching images, replacing type names with actual types etc
            job, default_seed = prepare_job(self.data)

            # collections that are passed between steps to share state
            results = []
            intermediate_results = {}
            shared_components = {}
            for step_data in job["steps"]:
                step = Step(step_data, default_seed)
                step.run(intermediate_results, shared_components)
                results.extend(step.results)  

            with open(os.path.join(output_dir, f"{job_id}.json"), 'w') as file:
                json.dump(self.data, file, indent=4)

            for i, result in enumerate(results):
                result.save(output_dir, f"{job_id}-{i}")        

            print("ok")

        except Exception as e:
            print(f"Error running job {self.data.get('id', 'unknown')}")
            print(e)


def prepare_job(input_job):
    if input_job is None:
        return {}, 0

    # modify the source dictionary with a default seed value
    # so that it will be captured when the arguments are saved
    input_job["seed"] = input_job.get("seed", torch.seed())    

    job = copy.deepcopy(input_job)

    realize_args(job)

    return job, input_job["seed"]
