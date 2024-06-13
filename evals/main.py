# main.py

from utils.helper_functions import load_config
import os
from evals.evals import main_run
from langchain.smith import RunEvalConfig, run_on_dataset
from langsmith import Client
import json

server = 'openai'
model = 'gpt-3.5-turbo-1106'
model_endpoint = None

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
load_config(config_path)

iterations = 40

if __name__ == "__main__":
    client = Client()

    profile_paths = [
        "profile1.json",
        "profile2.json",
        "profile3.json",
        "profile4.json"
    ]

    dataset_name = "Profile Evaluation"

    # Check if dataset exists
    datasets = client.list_datasets()
    dataset_id = None
    for ds in datasets:
        if ds.name == dataset_name:  # Access the attribute directly
            dataset_id = ds.id
            break

    if not dataset_id:
        # Create a new dataset if it does not exist
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Different Profiles for Evaluation",
        )
        dataset_id = dataset.id  # Access the attribute directly

    for profile_path in profile_paths:
        try:
            # Check if the file is empty
            if os.path.getsize(profile_path) == 0:
                raise ValueError(f"Profile file {profile_path} is empty")

            # Load the profile to create an example in the dataset
            with open(profile_path, 'r') as profile_file:
                profile = json.load(profile_file)

            # Each example must be unique and have inputs defined.
            # Outputs are optional
            client.create_example(
                inputs={"profile_path": profile_path},
                outputs=None,
                dataset_id=dataset_id,
            )

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {profile_path}: {e}")
        except Exception as e:
            print(f"Error processing file {profile_path}: {e}")

    eval_config = RunEvalConfig(
        evaluators=[
            "criteria",
            RunEvalConfig.Criteria(
                {
                    "cliche": "Are the exeriments cliche?"
                    "Respond Y if they are, N if they're entirely unique."
                }
            ),
            RunEvalConfig.Criteria(
                {
                    "specific": "Are the experiments specific? Do the experiments offer direct actionable advice relevant to the business?"
                    "Respond Y if they are, N if they're not specific"
                }
            ),
        ]
    )


    def llm_factory(inputs):
        profile_path = inputs["profile_path"]  # Extract the profile path
        experiments = main_run(inputs, server, model, model_endpoint, iterations, profile_file=profile_path)
        return experiments

    run_on_dataset(
        client=client,
        dataset_name=dataset_name,
        llm_or_chain_factory=llm_factory,
        evaluation=eval_config,
    )
