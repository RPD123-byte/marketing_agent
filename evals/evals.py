from agent_graph.graph import create_graph, compile_workflow
from utils.helper_functions import load_config
import json

def main_run(inputs, server='openai', model='gpt-3.5-turbo-1106', model_endpoint=None, iterations=40, profile_file=None):
    verbose = False

    print ("Creating graph and compiling workflow...")
    graph = create_graph(server=server, model=model, model_endpoint=model_endpoint, profile_file=profile_file)
    workflow = compile_workflow(graph)
    print ("Graph and workflow created.")

    while True:
        # query = input("Please enter your research question: ")
        # query = input("Are You Ready: ")
        query = "go"


        # if query.lower() == "exit":
        #     break

        dict_inputs = {"research_question": query}
        thread = {"configurable": {"thread_id": "4"}}
        limit = {"recursion_limit": iterations}

        # for event in workflow.stream(
        #     dict_inputs, thread, limit, stream_mode="values"
        #     ):
        #     if verbose:
        #         print("\nState Dictionary:", event)
        #     else:
        #         print("\n")

        for event in workflow.stream(
            dict_inputs, limit
            ):
            if verbose:
                print("\nState Dictionary:", event)
            else:
                print("\n")
        
        # Load the profile again to extract the updated experiments
        with open(profile_file, 'r') as profile_file:
            profile = json.load(profile_file)

        # Extract experiments from the profile
        experiments = profile.get("Experiments", {})

        return experiments


    