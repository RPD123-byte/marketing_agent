import json
import ast
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from models.openai_models import get_open_ai_json
from langgraph.checkpoint.sqlite import SqliteSaver
from agents.agents import (
    planner_agent, 
    researcher_agent, 
    reporter_agent, 
    reviewer_agent, 
    final_report, 
    industry_creator_agent,
    questions_generator_agent,
    questions_categorizer_agent,
    research_agent,
    experiments_generator_agent,
    experiments_scoring_agent,
    end_node
    )
from prompts.prompts import (
    reviewer_prompt_template, 
    planner_prompt_template, 
    researcher_prompt_template, 
    reporter_prompt_template,
    reviewer_guided_json,
    researcher_guided_json,
    planner_guided_json,
    industry_creator_prompt_template,
    industry_creator_guided_json,
    questions_generator_prompt_template,
    questions_generator_guided_json,
    questions_categorizer_prompt_template,
    questions_categorizer_guided_json,
    generate_outline_prompt_template,
    generate_outline_guided_json,
    experiments_generator_prompt_template,
    experiments_generator_guided_json,
    experiments_scoring_prompt_template,
    experiments_scoring_guided_json
    )
from tools.google_serper import get_google_serper
from tools.basic_scraper import scrape_website
from tools.background_identifier import match_industry
from states.state import AgentGraphState, get_agent_graph_state, state
# from utils.helper_functions import custom_print
from utils.pass_review import pass_review

def create_graph(server=None, model=None, stop=None, model_endpoint=None, profile_file=None):
    graph = StateGraph(AgentGraphState)

    # graph.add_node(
    #     "planner", 
    #     lambda state: planner_agent(
    #         state=state,
    #         research_question=state["research_question"],  
    #         feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"), 
    #         previous_plans=lambda: get_agent_graph_state(state=state, state_key="planner_all"),
    #         model=model,
    #         server=server,
    #         guided_json=planner_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint
    #     )
    # )

    # graph.add_node(
    #     "researcher",
    #     lambda state: researcher_agent(
    #         state=state,
    #         research_question=state["research_question"], 
    #         feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"), 
    #         previous_selections=lambda: get_agent_graph_state(state=state, state_key="researcher_all"), 
    #         serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
    #         model=model,
    #         server=server,
    #         guided_json=researcher_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint
    #     )
    # )

    # graph.add_node(
    #     "reporter", 
    #     lambda state: reporter_agent(
    #         state=state,
    #         research_question=state["research_question"], 
    #         feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"), 
    #         previous_reports=lambda: get_agent_graph_state(state=state, state_key="reporter_all"), 
    #         research=lambda: get_agent_graph_state(state=state, state_key="researcher_latest"),
    #         model=model,
    #         server=server,
    #         stop=stop,
    #         model_endpoint=model_endpoint
    #     )
    # )

    # graph.add_node(
    #     "reviewer", 
    #     lambda state: reviewer_agent(
    #         state=state,
    #         research_question=state["research_question"], 
    #         feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"), 
    #         planner=lambda: get_agent_graph_state(state=state, state_key="planner_latest"), 
    #         researcher=lambda: get_agent_graph_state(state=state, state_key="researcher_latest"), 
    #         reporter=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
    #         planner_agent=planner_prompt_template,
    #         researcher_agent=researcher_prompt_template,
    #         reporter_agent=reporter_prompt_template,
    #         serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
    #         model=model,
    #         server=server,
    #         guided_json=reviewer_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint
    #     )
    # )

    # graph.add_node(
    #     "serper_tool",
    #     lambda state: get_google_serper(
    #         state=state,
    #         plan=lambda: get_agent_graph_state(state=state, state_key="planner_latest")
    #     )
    # )

    # graph.add_node(
    #     "scraper_tool",
    #     lambda state: scrape_website(
    #         state=state,
    #         research=lambda: get_agent_graph_state(state=state, state_key="researcher_latest")
    #     )
    # )

    # graph.add_node(
    #     "final_report", 
    #     lambda state: final_report(
    #         state=state,
    #         final_response=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
    #         )
    # )

    # # Add edges to the graph
    # graph.set_entry_point("planner")
    # graph.set_finish_point("end")
    # graph.add_edge("planner", "serper_tool")
    # graph.add_edge("serper_tool", "researcher")
    # graph.add_edge("researcher", "scraper_tool")
    # graph.add_edge("scraper_tool", "reporter")
    # graph.add_edge("reporter", "reviewer")

    # graph.add_conditional_edges(
    #     "reviewer",
    #     lambda state: pass_review(state=state, model=model),
    # )ys

    # graph.add_edge("final_report", "end")

    graph.add_node(
        "background_identifier",
        lambda state: match_industry(
            state=state,
            profile_file=profile_file,
            business_data_file="business_data.json"
        )
    )

    graph.add_node(
        "industry_creator",
        lambda state: industry_creator_agent(
            state=state,
            prompt=industry_creator_prompt_template,
            model=model,
            server=server,
            guided_json=industry_creator_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            profile_file=profile_file
        )
    )

    graph.add_node(
        "questions_generator",
        lambda state: questions_generator_agent(
            state=state,
            prompt=questions_generator_prompt_template,
            model=model,
            server=server,
            guided_json=questions_generator_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            profile_file=profile_file
        )
    )

    graph.add_node(
        "questions_categorizer",
        lambda state: questions_categorizer_agent(
            state=state,
            prompt=questions_categorizer_prompt_template,
            model=model,
            server=server,
            guided_json=questions_categorizer_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            profile_file=profile_file
        )
    )

    graph.add_node(
        "research",
        lambda state: research_agent(
            state=state,
            prompt=generate_outline_prompt_template,
            model=model,
            server=server,
            guided_json=generate_outline_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            profile_file=profile_file
        )
    )

    graph.add_node(
        "experiments_generator",
        lambda state: experiments_generator_agent(
            state=state,
            prompt=experiments_generator_prompt_template,
            model=model,
            server=server,
            guided_json=experiments_generator_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            profile_file=profile_file
        )
    )

    graph.add_node("set_next_category", lambda state: state)

    graph.add_node(
        "experiments_scoring",
        lambda state: experiments_scoring_agent(
            state=state,
            prompt=experiments_scoring_prompt_template,
            model=model,
            server=server,
            guided_json=experiments_scoring_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            profile_file=profile_file
        )
    )

    graph.add_node("end", lambda state: end_node(state=state))


    graph.set_entry_point("background_identifier")
    graph.set_finish_point("end")




    # Conditional edges to decide if we need to create industry data or generate questions
    graph.add_conditional_edges(
        "background_identifier",
        lambda state: "industry_creator" if not json.loads(state["checker_response"][-1].content)["data"] else "questions_generator"
    )

    # Main flow
    graph.add_edge("industry_creator", "background_identifier")
    graph.add_edge("questions_generator", "questions_categorizer")
    

    def next_research_or_experiment(state: AgentGraphState):
        categorized_questions = json.loads(state["categorized_questions"][-1].content)["Categories"]
        
        # Ensure current_category_index is initialized
        if state.get("current_category_index") is None:
            state["current_category_index"] = 0

        # Check if all categories have been processed
        if state["current_category_index"] >= len(categorized_questions):
            return "experiments_generator"
        
        return "research"



    
    graph.add_conditional_edges("set_next_category", next_research_or_experiment)
    
    graph.add_edge("questions_categorizer", "set_next_category")
    graph.add_edge("research", "set_next_category")

    graph.add_edge("experiments_generator", "experiments_scoring")
    graph.add_edge("experiments_scoring", "end")
    return graph

def compile_workflow(graph):
    # memory = SqliteSaver.from_conn_string(":memory:")  # Here we only save in-memory
    # workflow = graph.compile(checkpointer=memory, interrupt_before=["end"])
    workflow = graph.compile()
    return workflow