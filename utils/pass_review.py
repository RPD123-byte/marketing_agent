from states.state import AgentGraphState
from langchain_core.messages import HumanMessage
import json

# Define the edges in the agent graph
def pass_review(state: AgentGraphState, model=None):
    review_list = state["reviewer_response"]
    if review_list:
        review = review_list[-1]
    else:
        review = "No review"

    if review != "No review":
        if isinstance(review, HumanMessage):
            review_content = review.content
        else:
            review_content = review
        
        # review_data = ast.literal_eval(review_content)
        # review_data = json.loads(review_content)
        review_data = json.loads(review_content)
        next_agent = review_data["suggest_next_agent"]
    else:
        next_agent = "end"

    # messages = [
    #     {
    #         "role":"system","content":
    #         """
    #         Your purpose is to route the conversation to the appropriate agent based on the reviewer's feedback.
    #         You do this by providing a response in the form of a dictionary.
    #         For the first key, "review_pass", you must provide a value of "True" or "False".
    #         If the reviewer approves, return True. Otherwise, return False.

    #         For the second key, "next_agent", you must provide the name of the agent to route the conversation to.
    #         Your choices are: planner, researcher, reporter, or final_report.
    #         You must select only ONE of these options.

    #         if you pass the review, you MUST select "final_report".

    #         Your response must be a json:
    #         {
    #             "review_pass": "True/False",
    #             "next_agent": "planner/researcher/reporter/final_report"
    #         }
    #         """
    #     },
    #     {"role":"user", "content": f"Reviewer's feedback: {review}. Respond with json"}
    # ]

    # llm = get_open_ai_json(model=model)
    # ai_msg = llm.invoke(messages)

    # review_dict = ast.literal_eval(ai_msg.content)

    # # To handle abnormally formatted responses
    # try:
    #     next_agent = review_dict["next_agent"]
    #     print(f"\n\nReview Passed: {review_dict['review_pass']}\n\nHanding over to {next_agent}\n")

    # except KeyError as e:
    #     next_agent = "end"
    #     print(f"Error: {e}\n\n Exiting agent flow {next_agent}\n")

    return next_agent