import json
import yaml
import os
from termcolor import colored
from models.openai_models import get_open_ai, get_open_ai_json
from models.ollama_models import OllamaModel, OllamaJSONModel
from models.vllm_models import VllmJSONModel, VllmModel
from prompts.prompts import (
    planner_prompt_template,
    researcher_prompt_template,
    reporter_prompt_template,
    reviewer_prompt_template,
    industry_creator_prompt_template,
    questions_generator_prompt_template,
    questions_categorizer_prompt_template,
    generate_outline_prompt_template,
    experiments_generator_prompt_template,
    experiments_scoring_prompt_template
)
from utils.helper_functions import get_current_utc_datetime, check_for_content, generate_report_from_outline
from states.state import AgentGraphState 
from langchain_core.messages import SystemMessage
import langsmith



def industry_creator_agent(state: AgentGraphState, prompt=industry_creator_prompt_template, model=None, server=None, guided_json=None, stop=None, model_endpoint=None, profile_file=None):
    # Load the industry name from profile.json
    with open(profile_file, 'r') as f:
        profile_data = json.load(f)
    
    industry_name = profile_data.get("Industry", "")

    datetime = get_current_utc_datetime()
    
    industry_creator_prompt = prompt.format(
        industry_name=industry_name,
        datetime=datetime
    )

    messages = [
        {"role": "system", "content": industry_creator_prompt},
        {"role": "user", "content": f"Create a profile for the {industry_name} industry."}
    ]

    if server == 'openai':
        llm = get_open_ai_json(model=model)
    if server == 'ollama':
        llm = OllamaJSONModel(model=model)
    if server == 'vllm':
        llm = VllmJSONModel(
            model=model, 
            guided_json=guided_json,
            stop=stop,
            model_endpoint=model_endpoint
            )
        
    ai_msg = llm.invoke(messages)

    response = ai_msg.content

    # Parse the response to ensure it's valid JSON
    try:
        new_industry_profile = json.loads(response)
    except json.JSONDecodeError as e:
        state = {**state, "industry_creator_response": f"Failed to parse response: {str(e)}"}
        return state

    # Load the current business data
    with open('business_data.json', 'r') as f:
        business_data = json.load(f)

    # Add the new industry profile to the business data
    business_data.append(new_industry_profile)

    # Save the updated business data
    with open('business_data.json', 'w') as f:
        json.dump(business_data, f, indent=4)

    state = {**state, "industry_creator_response": response}

    print(colored(f"Industry Creator 🏭: {response}", 'magenta'))

    return state


def questions_generator_agent(state: AgentGraphState, prompt=questions_generator_prompt_template, model=None, server=None, guided_json=None, stop=None, model_endpoint=None, profile_file=None):

    # Load the industry data from the latest checker_response
    industry_data = json.loads(state["checker_response"][-1].content)["data"][0]

    industry_name = industry_data.get("Industry Name", "")
    main_focuses = industry_data.get("Main Focuses", {})

    # Load the background information from profile.json
    with open(profile_file, 'r') as f:
        profile_data = json.load(f)
    
    background_info = profile_data.get("Background", {})

    datetime = get_current_utc_datetime()
    
    questions_generator_prompt = prompt.format(
        industry_name=industry_name,
        main_focuses=json.dumps(main_focuses, indent=4),
        background_info=json.dumps(background_info, indent=4),
        datetime=datetime
    )

    messages = [
        {"role": "system", "content": questions_generator_prompt},
        {"role": "user", "content": f"Generate a list of questions that can be answered through internet search for the {industry_name} industry."}
    ]

    if server == 'openai':
        llm = get_open_ai_json(model=model)
    if server == 'ollama':
        llm = OllamaJSONModel(model=model)
    if server == 'vllm':
        llm = VllmJSONModel(
            model=model, 
            guided_json=guided_json,
            stop=stop,
            model_endpoint=model_endpoint
        )
        
    ai_msg = llm.invoke(messages)

    response = ai_msg.content

    # Parse the response to ensure it's valid JSON
    try:
        internet_questions = json.loads(response)
    except json.JSONDecodeError as e:
        state = {**state, "internet_questions": [SystemMessage(content=f"Failed to parse response: {str(e)}")]}
        return state

    state["internet_questions"].append(SystemMessage(content=response))

    print(colored(f"Questions Generator 🤔: {response}", 'green'))

    # Update the profile.json with the new internet questions
    try:
        profile_data['Internet Questions'] = internet_questions.get("Internet Questions", [])
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=4)
    except Exception as e:
        print(colored(f"Failed to update profile.json: {str(e)}", 'red'))

    return state



def questions_categorizer_agent(state: AgentGraphState, prompt=questions_categorizer_prompt_template, model=None, server=None, guided_json=None, stop=None, model_endpoint=None, profile_file=None):
    # Load the internet questions from the state
    internet_questions = json.loads(state["internet_questions"][-1].content)["Internet Questions"]

    datetime = get_current_utc_datetime()

    questions_categorizer_prompt = prompt.format(
        internet_questions=json.dumps(internet_questions, indent=4),
        datetime=datetime
    )

    messages = [
        {"role": "system", "content": questions_categorizer_prompt},
        {"role": "user", "content": f"Categorize the questions based on similarity for the {datetime}."}
    ]

    if server == 'openai':
        llm = get_open_ai_json(model=model)
    if server == 'ollama':
        llm = OllamaJSONModel(model=model)
    if server == 'vllm':
        llm = VllmJSONModel(
            model=model, 
            guided_json=guided_json,
            stop=stop,
            model_endpoint=model_endpoint
        )
        
    ai_msg = llm.invoke(messages)

    response = ai_msg.content

    # Parse the response to ensure it's valid JSON
    try:
        categorized_questions = json.loads(response)
    except json.JSONDecodeError as e:
        state = {**state, "categorized_questions": [SystemMessage(content=f"Failed to parse response: {str(e)}")]}
        return state

    state["categorized_questions"].append(SystemMessage(content=response))

    print(colored(f"Categorized Questions 🤔: {response}", 'green'))

    # Load the profile.json
    try:
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)

        # Update the profile.json with the new categorized questions
        profile_data['Categorized Questions'] = categorized_questions.get("Categories", {})
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=4)
    except Exception as e:
        print(colored(f"Failed to update profile.json: {str(e)}", 'red'))

    return state



def research_agent(state: AgentGraphState, prompt=generate_outline_prompt_template, model=None, server=None, guided_json=None, stop=None, model_endpoint=None, profile_file=None):
    # Load the categorized questions from the state
    categorized_questions = json.loads(state["categorized_questions"][-1].content)["Categories"]

    # Ensure current_category_index is initialized
    if state.get("current_category_index") is None:
        state["current_category_index"] = 0

    current_index = state["current_category_index"]

    # Check if we've processed all categories
    if current_index >= len(categorized_questions):
        return state

    category = list(categorized_questions.keys())[current_index]
    questions = categorized_questions[category]

    datetime = get_current_utc_datetime()

    questions_str = "\n".join(questions)
    outline_prompt = prompt.format(
        questions=questions_str,
        datetime=datetime
    )

    messages = [
        {"role": "system", "content": outline_prompt},
        {"role": "user", "content": f"Generate a detailed report outline for the category: {category}"}
    ]

    if server == 'openai':
        llm = get_open_ai_json(model=model)
    if server == 'ollama':
        llm = OllamaJSONModel(model=model)
    if server == 'vllm':
        llm = VllmJSONModel(
            model=model, 
            guided_json=guided_json,
            stop=stop,
            model_endpoint=model_endpoint
        )

    ai_msg = llm.invoke(messages)

    response = ai_msg.content

    # Parse the response to ensure it's valid JSON
    try:
        report_outline = json.loads(response)["Outline"]
    except json.JSONDecodeError as e:
        state = {**state, "report_outlines": [SystemMessage(content=f"Failed to parse response: {str(e)}")]}
        return state

    state["report_outlines"].append(SystemMessage(content=response))
    
    print(colored(f"Reports 💎: {response}", 'blue'))

    # Create the report based on the outline
    report = generate_report_from_outline(report_outline)

    # Load the business_data.json
    try:
        with open('business_data.json', 'r') as f:
            business_data = json.load(f)

        # Find the corresponding industry and update the background with the report
        profile_data = {}
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)
            
        industry_name = profile_data.get("Industry", "")

        for industry in business_data:
            if industry.get("Industry Name", "").lower() == industry_name.lower():
                if "Background" not in industry:
                    industry["Background"] = {}
                industry["Background"][category] = report

        with open('business_data.json', 'w') as f:
            json.dump(business_data, f, indent=4)
    except Exception as e:
        print(colored(f"Failed to update business_data.json: {str(e)}", 'red'))

    # Update the current_category_index for the next iteration
    state["current_category_index"] += 1

    return state



def experiments_generator_agent(state: AgentGraphState, prompt=experiments_generator_prompt_template, model=None, server=None, guided_json=None, stop=None, model_endpoint=None, profile_file=None):
    # Load the industry name and main focus from profile.json
    with open(profile_file, 'r') as f:
        profile_data = json.load(f)
    industry_name = profile_data.get("Industry", "")
    main_focus = profile_data.get("Main Focus", "")

    # Load the relevant industry data from business_data.json
    with open('business_data.json', 'r') as f:
        business_data = json.load(f)
    industry_data = next((industry for industry in business_data if industry.get("Industry Name", "").lower() == industry_name.lower()), {})
    main_focus_data = industry_data.get("Main Focuses", {}).get(main_focus, {})

    context = json.dumps(main_focus_data, indent=4)

    # Debugging information
    print(f"Context: {context}")
    print(f"Main Focus: {main_focus}")

    experiments_generator_prompt = prompt.format(
        context=context,
        main_focus=main_focus
    )

    messages = [
        {"role": "system", "content": experiments_generator_prompt},
        {"role": "user", "content": f"Generate several experiments for the main focus area: {main_focus}"}
    ]

    if server == 'openai':
        llm = get_open_ai_json(model=model)
    elif server == 'ollama':
        llm = OllamaJSONModel(model=model)
    elif server == 'vllm':
        llm = VllmJSONModel(
            model=model, 
            guided_json=guided_json,
            stop=stop,
            model_endpoint=model_endpoint
        )

    ai_msg = llm.invoke(messages)

    response = ai_msg.content

    # Parse the response to ensure it's valid JSON
    try:
        experiments = json.loads(response)["Experiments"]
    except json.JSONDecodeError as e:
        state = {**state, "experiments": [SystemMessage(content=f"Failed to parse response: {str(e)}")]}
        return state

    state["experiments"].append(SystemMessage(content=response))

    print(colored(f"Experiments 🟡: {response}", 'yellow'))

    # Add the experiments to the profile.json under the relevant industry and main focus
    try:
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)

        if "Experiments" not in profile_data:
            profile_data["Experiments"] = {}
        if industry_name not in profile_data["Experiments"]:
            profile_data["Experiments"][industry_name] = {}
        if main_focus not in profile_data["Experiments"][industry_name]:
            profile_data["Experiments"][industry_name][main_focus] = []
        profile_data["Experiments"][industry_name][main_focus].extend(experiments)

        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=4)
    except Exception as e:
        print(colored(f"Failed to update profile.json: {str(e)}", 'red'))

    return state



def experiments_scoring_agent(state: AgentGraphState, prompt=experiments_scoring_prompt_template, model=None, server=None, guided_json=None, stop=None, model_endpoint=None, profile_file=None):
    experiments = [json.loads(msg.content) for msg in state["experiments"]]

    print("Experiments extracted from state:", experiments)

    # Flatten the experiments list if it's nested under "Experiments"
    if "Experiments" in experiments[0]:
        experiments = experiments[0]["Experiments"]

    formatted_experiments = json.dumps(experiments, indent=4)
    print("Formatted experiments for prompt:", formatted_experiments)

    experiments_scoring_prompt = prompt.format(experiments=formatted_experiments)
    
    messages = [
        {"role": "system", "content": experiments_scoring_prompt},
        {"role": "user", "content": "Please score the provided experiments based on Impact, Confidence, and Ease."}
    ]
    
    print("Experiments scoring prompt:", experiments_scoring_prompt)

    if server == 'openai':
        llm = get_open_ai_json(model=model)
    if server == 'ollama':
        llm = OllamaJSONModel(model=model)
    if server == 'vllm':
        llm = VllmJSONModel(
            model=model, 
            guided_json=guided_json,
            stop=stop,
            model_endpoint=model_endpoint
        )

    ai_msg = llm.invoke(messages)
    response = ai_msg.content

    print("Response from LLM:", response)

    # Parse the response to ensure it's valid JSON
    try:
        scored_experiments = json.loads(response)["ScoredExperiments"]
        print("Scored experiments parsed from response:", scored_experiments)
    except json.JSONDecodeError as e:
        print("Failed to parse response:", str(e))
        state = {**state, "scored_experiments": [SystemMessage(content=f"Failed to parse response: {str(e)}")]}
        return state

    # Merge scores into the original experiments
    for i in range(len(experiments)):
        experiments[i].update(scored_experiments[i])
    
    print("Experiments after merging scores:", experiments)

    state["experiments"] = [SystemMessage(content=json.dumps(exp)) for exp in experiments]

    print("Updated state with scored experiments:", state["experiments"])

    # Add the experiments with scores to the profile.json under the relevant industry and main focus
    try:
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)
        
        industry_name = profile_data.get("Industry", "")
        main_focus = profile_data.get("Main Focus", "")

        print(f"Updating profile.json for industry: {industry_name}, main focus: {main_focus}")

        if "Experiments" not in profile_data:
            profile_data["Experiments"] = {}
        if industry_name not in profile_data["Experiments"]:
            profile_data["Experiments"][industry_name] = {}
        if main_focus not in profile_data["Experiments"][industry_name]:
            profile_data["Experiments"][industry_name][main_focus] = []
        profile_data["Experiments"][industry_name][main_focus] = experiments

        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=4)
        
        print("Updated profile.json successfully")
    except Exception as e:
        print(colored(f"Failed to update profile.json: {str(e)}", 'red'))

    return state









def planner_agent(state:AgentGraphState, research_question, prompt=planner_prompt_template, model=None, feedback=None, previous_plans=None, server=None, guided_json=None, stop=None, model_endpoint=None):

    feedback_value = feedback() if callable(feedback) else feedback
    previous_plans_value = previous_plans() if callable(previous_plans) else previous_plans

    feedback_value = check_for_content(feedback_value)
    previous_plans_value = check_for_content(previous_plans_value)

    planner_prompt = prompt.format(
        feedback=feedback_value,
        previous_plans=previous_plans_value,
        datetime=get_current_utc_datetime()
    )


    messages = [
        {"role": "system", "content": planner_prompt},
        {"role": "user", "content": f"research question: {research_question}"}
    ]

    if server == 'openai':
        llm = get_open_ai_json(model=model)
    if server == 'ollama':
        llm = OllamaJSONModel(model=model)
    if server == 'vllm':
        llm = VllmJSONModel(
            model=model, 
            guided_json=guided_json,
            stop=stop,
            model_endpoint=model_endpoint
            )

    ai_msg = llm.invoke(messages)

    response = ai_msg.content

    state = {**state, "planner_response": response}

    print(colored(f"Planner 👩🏿‍💻: {response}", 'cyan'))

    return state

def researcher_agent(state:AgentGraphState, research_question, prompt=researcher_prompt_template, model=None, feedback=None, previous_selections=None, serp=None, server=None, guided_json=None, stop=None, model_endpoint=None):

    feedback_value = feedback() if callable(feedback) else feedback
    previous_selections_value = previous_selections() if callable(previous_selections) else previous_selections

    feedback_value = check_for_content(feedback_value)
    previous_selections_value = check_for_content(previous_selections_value)

    researcher_prompt = prompt.format(
        feedback=feedback_value,
        previous_selections=previous_selections_value,
        serp=serp().content,
        datetime=get_current_utc_datetime()
    )

    messages = [
        {"role": "system", "content": researcher_prompt},
        {"role": "user", "content": f"research question: {research_question}"}
    ]

    if server == 'openai':
        llm = get_open_ai_json(model=model)
    if server == 'ollama':
        llm = OllamaJSONModel(model=model)
    if server == 'vllm':
        llm = VllmJSONModel(
            model=model, 
            model_endpoint=model_endpoint, 
            guided_json=guided_json, 
            stop=stop
            )

    ai_msg = llm.invoke(messages)

    response = ai_msg.content

    print(colored(f"Researcher 🧑🏼‍💻: {response}", 'green'))

    state = {**state, "researcher_response": response}

    return state

def reporter_agent(state:AgentGraphState, research_question, prompt=reporter_prompt_template, model=None, feedback=None, previous_reports=None, research=None, server=None, stop=None, model_endpoint=None):

    feedback_value = feedback() if callable(feedback) else feedback
    previous_reports_value = previous_reports() if callable(previous_reports) else previous_reports
    research_value = research() if callable(research) else research

    feedback_value = check_for_content(feedback_value)
    previous_reports_value = check_for_content(previous_reports_value)
    research_value = check_for_content(research_value)
    
    reporter_prompt = prompt.format(
        feedback=feedback_value,
        previous_reports=previous_reports_value,
        datetime=get_current_utc_datetime(),
        research=research_value
    )

    messages = [
        {"role": "system", "content": reporter_prompt},
        {"role": "user", "content": f"research question: {research_question}"}
    ]

    if server == 'openai':
        llm = get_open_ai(model=model)
    if server == 'ollama':
        llm = OllamaModel(model=model)
    if server == 'vllm':
        llm = VllmModel(
            model=model, 
            model_endpoint=model_endpoint, 
            stop=stop
            )

    ai_msg = llm.invoke(messages)

    response = ai_msg.content
    
    print(colored(f"Reporter 👨‍💻: {response}", 'yellow'))

    state = {**state, "reporter_response": response}

    return state

def reviewer_agent(
        state:AgentGraphState,
        research_question,
        prompt=reviewer_prompt_template, 
        model=None, 
        planner=None, 
        researcher=None, 
        reporter=None, 
        planner_agent=None, 
        researcher_agent=None, 
        reporter_agent=None,
        feedback=None,
        serp=None,
        server=None,
        guided_json=None,
        stop=None,
        model_endpoint=None
        ):
    
    planner_value = planner() if callable(planner) else planner
    researcher_value = researcher() if callable(researcher) else researcher
    reporter_value = reporter() if callable(reporter) else reporter
    planner_agent_value = planner_agent
    researcher_agent_value = researcher_agent
    reporter_agent_value = reporter_agent
    feedback_value = feedback() if callable(feedback) else feedback

    planner_value = check_for_content(planner_value)
    researcher_value = check_for_content(researcher_value)
    reporter_value = check_for_content(reporter_value)
    feedback_value = check_for_content(feedback_value)
    
    reviewer_prompt = prompt.format(
        planner = planner_value,
        researcher=researcher_value,
        reporter=reporter_value,
        planner_responsibilities=planner_agent_value,
        researcher_responsibilities=researcher_agent_value,
        reporter_responsibilities=reporter_agent_value,
        feedback=feedback_value,
        datetime=get_current_utc_datetime(),
        serp=serp().content
    )

    messages = [
        {"role": "system", "content": reviewer_prompt},
        {"role": "user", "content": f"research question: {research_question}"}
    ]

    if server == 'openai':
        llm = get_open_ai_json(model=model)
    if server == 'ollama':
        llm = OllamaJSONModel(model=model)
    if server == 'vllm':
        llm = VllmJSONModel(
            model=model, 
            guided_json=guided_json, 
            stop=stop, 
            model_endpoint=model_endpoint
            )


    ai_msg = llm.invoke(messages)

    response = ai_msg.content

    print(colored(f"Reviewer 👩🏽‍⚖️: {response}", 'magenta'))

    state = {**state, "reviewer_response": response}

    return state


def final_report(state:AgentGraphState, final_response=None):
    final_response_value = final_response() if callable(final_response) else final_response

    response = final_response_value.content

    print(colored(f"Final Report 📝: {response}", 'blue'))

    state = {**state, "final_reports": response}

    return state

def end_node(state:AgentGraphState):
    state = {**state, "end_chain": "end_chain"}
    return state


    