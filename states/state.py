from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages

class AgentGraphState(TypedDict):
    research_question: str
    planner_response: Annotated[list, add_messages]
    researcher_response: Annotated[list, add_messages]
    reporter_response: Annotated[list, add_messages]
    reviewer_response: Annotated[list, add_messages]
    serper_response: Annotated[list, add_messages]
    scraper_response: Annotated[list, add_messages]
    final_reports: Annotated[list, add_messages]
    end_chain: Annotated[list, add_messages]
    checker_response: Annotated[list, add_messages]
    industry_creator_response: Annotated[list, add_messages]
    uncertain_questions: Annotated[list, add_messages]
    internet_questions: Annotated[list, add_messages]
    categorized_questions: Annotated[list, add_messages]
    report_outlines: Annotated[list, add_messages]
    current_category_index: Optional[int]
    experiments: Annotated[list, add_messages]
    main_focus: Optional[str]
    scored_experiments: Annotated[list, add_messages]  # New field for scored experiments

# Define the nodes in the agent graph
def get_agent_graph_state(state: AgentGraphState, state_key: str):
    if state_key == "planner_all":
        return state["planner_response"]
    elif state_key == "planner_latest":
        if state["planner_response"]:
            return state["planner_response"][-1]
        else:
            return state["planner_response"]
    
    elif state_key == "researcher_all":
        return state["researcher_response"]
    elif state_key == "researcher_latest":
        if state["researcher_response"]:
            return state["researcher_response"][-1]
        else:
            return state["researcher_response"]
    
    elif state_key == "reporter_all":
        return state["reporter_response"]
    elif state_key == "reporter_latest":
        if state["reporter_response"]:
            return state["reporter_response"][-1]
        else:
            return state["reporter_response"]
    
    elif state_key == "reviewer_all":
        return state["reviewer_response"]
    elif state_key == "reviewer_latest":
        if state["reviewer_response"]:
            return state["reviewer_response"][-1]
        else:
            return state["reviewer_response"]
        
    elif state_key == "serper_all":
        return state["serper_response"]
    elif state_key == "serper_latest":
        if state["serper_response"]:
            return state["serper_response"][-1]
        else:
            return state["serper_response"]
    
    elif state_key == "scraper_all":
        return state["scraper_response"]
    elif state_key == "scraper_latest":
        if state["scraper_response"]:
            return state["scraper_response"][-1]
        else:
            return state["scraper_response"]
    
    elif state_key == "checker_all":
        return state["checker_response"]
    elif state_key == "checker_latest":
        if state["checker_response"]:
            return state["checker_response"][-1]
        else:
            return state["checker_response"]
    
    elif state_key == "industry_creator_all":
        return state["industry_creator_response"]
    elif state_key == "industry_creator_latest":
        if state["industry_creator_response"]:
            return state["industry_creator_response"][-1]
        else:
            return state["industry_creator_response"]
    
    elif state_key == "uncertain_all":
        return state["uncertain_questions"]
    elif state_key == "uncertain_latest":
        if state["uncertain_questions"]:
            return state["uncertain_questions"][-1]
        else:
            return state["uncertain_questions"]
    
    elif state_key == "internet_all":
        return state["internet_questions"]
    elif state_key == "internet_latest":
        if state["internet_questions"]:
            return state["internet_questions"][-1]
        else:
            return state["internet_questions"]
    
    elif state_key == "categorized_all":
        return state["categorized_questions"]
    elif state_key == "categorized_latest":
        if state["categorized_questions"]:
            return state["categorized_questions"][-1]
        else:
            return state["categorized_questions"]
    
    elif state_key == "reports_all":
        return state["report_outlines"]
    elif state_key == "reports_latest":
        if state["report_outlines"]:
            return state["report_outlines"][-1]
        else:
            return state["report_outlines"]
    
    elif state_key == "experiments_all":
        return state["experiments"]
    elif state_key == "experiments_latest":
        if state["experiments"]:
            return state["experiments"][-1]
        else:
            return state["experiments"]
    
    elif state_key == "main_focus":
        return state["main_focus"]
    
    elif state_key == "scored_experiments_all":
        return state["scored_experiments"]
    elif state_key == "scored_experiments_latest":
        if state["scored_experiments"]:
            return state["scored_experiments"][-1]
        else:
            return state["scored_experiments"]
    
    else:
        return None

state = {
    "research_question": "",
    "planner_response": [],
    "researcher_response": [],
    "reporter_response": [],
    "reviewer_response": [],
    "serper_response": [],
    "scraper_response": [],
    "final_reports": [],
    "end_chain": [],
    "checker_response": [],
    "industry_creator_response": [],
    "uncertain_questions": [],
    "internet_questions": [],
    "categorized_questions": [],
    "report_outlines": [],
    "current_category_index": 0,
    "experiments": [],
    "main_focus": None,
    "scored_experiments": []  # Initialize the new field
}
