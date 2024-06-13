from agent_graph.graph import create_graph, compile_workflow

# server = 'ollama'
# model = 'llama3:instruct'
# model_endpoint = None

server = 'openai'
model = 'gpt-3.5-turbo-1106'
model_endpoint = None

# server = 'vllm'
# model = 'meta-llama/Meta-Llama-3-70B-Instruct' # full HF path
# runpod_endpoint = 'https://t3o6jzhg3zqci3-8000.proxy.runpod.net/' 
# model_endpoint = runpod_endpoint + 'v1/chat/completions'
# stop = "<|end_of_text|>"

iterations = 40

print ("Creating graph and compiling workflow...")
graph = create_graph(server=server, model=model, model_endpoint=model_endpoint, profile_file="profile2.json")
workflow = compile_workflow(graph)
print ("Graph and workflow created.")


if __name__ == "__main__":
    verbose = False

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

    