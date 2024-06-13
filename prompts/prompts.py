industry_creator_prompt_template = """
You are an industry creator. Your responsibility is to create a comprehensive profile for a given industry if it doesn't already exist in the business data.
The profile should include the following sections: Industry Name, Main Focuses (with specific strategies for growth), and Background information.

Focus on creating detailed and relevant strategies and background information for the given industry. Each focus area should include more than two strategies, and the provided examples are just that - examples. The LLM should generate the appropriate number of strategies with descriptive names for each focus area.

Here is the industry name you need to create a profile for:
Industry: {industry_name}

Current date and time:
{datetime}

Your response must take the following JSON format:

{{
    "Industry Name": "{industry_name}",
    "Main Focuses": {{
        "Focus Area 1": {{
            "Strategy Name 1": "Description of Strategy 1",
            "Strategy Name 2": "Description of Strategy 2",
            ...
        }},
        "Focus Area 2": {{
            "Strategy Name 1": "Description of Strategy 1",
            "Strategy Name 2": "Description of Strategy 2",
            "Strategy Name 3": "Description of Strategy 3",
            ...
        }}
    }},
    "Background": {{
        "Market Size": "Description of the market size",
        "Number of Competitors": "Description of the number of competitors",
        "Consumer Trends": "Description of consumer trends",
        "Challenges": "Description of challenges",
        "Opportunities": "Description of opportunities"
    }}
}}
"""


industry_creator_guided_json = {
    "type": "object",
    "properties": {
        "Industry Name": {
            "type": "string",
            "description": "The name of the industry"
        },
        "Main Focuses": {
            "type": "object",
            "description": "The main focus areas and strategies for the industry",
            "properties": {
                "Focus Area 1": {
                    "type": "object",
                    "properties": {
                        "Strategy 1": {"type": "string"},
                        "Strategy 2": {"type": "string"}
                    },
                    "required": ["Strategy 1", "Strategy 2"]
                },
                "Focus Area 2": {
                    "type": "object",
                    "properties": {
                        "Strategy 1": {"type": "string"},
                        "Strategy 2": {"type": "string"}
                    },
                    "required": ["Strategy 1", "Strategy 2"]
                }
            }
        },
        "Background": {
            "type": "object",
            "description": "Background information about the industry",
            "properties": {
                "Market Size": {"type": "string"},
                "Number of Competitors": {"type": "string"},
                "Consumer Trends": {"type": "string"},
                "Challenges": {"type": "string"},
                "Opportunities": {"type": "string"}
            },
            "required": ["Market Size", "Number of Competitors", "Consumer Trends", "Challenges", "Opportunities"]
        }
    },
    "required": ["Industry Name", "Main Focuses", "Background"]
}


questions_generator_prompt_template = """
You are a strategic planner. Your task is to generate questions that can be answered through internet search based on the main focus areas of the business. Avoid questions that are specific to the business itself, such as "How effective have previous loyalty programs been in retaining customers?"

Industry: {industry_name}
Main Focuses: {main_focuses}

Given the main focus areas, generate a list of specific questions that can be answered through internet search to create effective experiments for growth. Each question should be detailed and aimed at understanding the broader industry and market context.

Here is the background information about the business:
{background_info}

Your response must be in the following JSON format:

{{
    "Internet Questions": [
        "Question 1",
        "Question 2",
        ...
    ]
}}
"""

questions_generator_guided_json = {
    "type": "object",
    "properties": {
        "Internet Questions": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of questions that can be answered through internet search"
        }
    },
    "required": ["Internet Questions"]
}



questions_categorizer_prompt_template = """
You are a strategic analyst. Your task is to categorize a list of questions into broad groups based on their similarity. Group questions into high-level categories that cover general themes rather than very specific topics.

Here are the questions:
{internet_questions}

Your response must be in the following JSON format:

{{
    "Categories": {{
        "Category 1": [
            "Question 1",
            "Question 2",
            ...
        ],
        "Category 2": [
            "Question 3",
            "Question 4",
            ...
        ],
        ...
    }}
}}
"""

questions_categorizer_guided_json = {
    "type": "object",
    "properties": {
        "Categories": {
            "type": "object",
            "description": "Broadly categorized questions based on their similarity",
            "patternProperties": {
                ".*": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        }
    },
    "required": ["Categories"]
}


generate_outline_prompt_template = """
You are an expert research assistant. Generate a detailed outline for a report based on the following questions:
{questions}

Your response must be in the following JSON format:

{{
    "Outline": {{
        "Title": "Generated Report",
        "Sections": [
            {{
                "Section Title": "Section 1",
                "Content": [
                    {{
                        "Subsection Title": "Subsection 1.1",
                        "Content": "Content of subsection 1.1"
                    }},
                    ...
                ]
            }},
            ...
        ]
    }}
}}
"""


generate_outline_guided_json = {
    "type": "object",
    "properties": {
        "Outline": {
            "type": "object",
            "properties": {
                "Title": {"type": "string"},
                "Sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Section Title": {"type": "string"},
                            "Content": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "Subsection Title": {"type": "string"},
                                        "Content": {"type": "string"}
                                    },
                                    "required": ["Subsection Title", "Content"]
                                }
                            }
                        },
                        "required": ["Section Title", "Content"]
                    }
                }
            },
            "required": ["Title", "Sections"]
        }
    },
    "required": ["Outline"]
}


experiments_generator_prompt_template = """
You are an expert in designing business experiments. Based on the provided context, generate a list of exactly five experiments that the business could carry out to grow in the main focus area of {main_focus}. Each experiment should include a brief, descriptive name that reflects its core idea, a detailed description addressing the who, what, where, when, why, and how of the experiment, a clear hypothesis outlining the expected cause and effect, and a list of specific metrics to be measured to evaluate the outcome of the experiment.

Context: {context}

Your response must be in the following JSON format:

{{
    "Experiments": [
        {{
            "Name": "Brief and descriptive name of Experiment 1",
            "Description": "Detailed description of Experiment 1 addressing the who, what, where, when, why, and how",
            "Hypothesis": "Clear hypothesis for Experiment 1 outlining the expected cause and effect",
            "Metrics": ["Metric 1", "Metric 2", "Metric 3"]
        }},
        {{
            "Name": "Brief and descriptive name of Experiment 2",
            "Description": "Detailed description of Experiment 2 addressing the who, what, where, when, why, and how",
            "Hypothesis": "Clear hypothesis for Experiment 2 outlining the expected cause and effect",
            "Metrics": ["Metric 1", "Metric 2", "Metric 3"]
        }},
        {{
            "Name": "Brief and descriptive name of Experiment 3",
            "Description": "Detailed description of Experiment 3 addressing the who, what, where, when, why, and how",
            "Hypothesis": "Clear hypothesis for Experiment 3 outlining the expected cause and effect",
            "Metrics": ["Metric 1", "Metric 2", "Metric 3"]
        }},
        {{
            "Name": "Brief and descriptive name of Experiment 4",
            "Description": "Detailed description of Experiment 4 addressing the who, what, where, when, why, and how",
            "Hypothesis": "Clear hypothesis for Experiment 4 outlining the expected cause and effect",
            "Metrics": ["Metric 1", "Metric 2", "Metric 3"]
        }},
        {{
            "Name": "Brief and descriptive name of Experiment 5",
            "Description": "Detailed description of Experiment 5 addressing the who, what, where, when, why, and how",
            "Hypothesis": "Clear hypothesis for Experiment 5 outlining the expected cause and effect",
            "Metrics": ["Metric 1", "Metric 2", "Metric 3"]
        }}
    ]
}}
"""



experiments_generator_guided_json = {
    "type": "object",
    "properties": {
        "Experiments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Name": {"type": "string"},
                    "Description": {"type": "string"},
                    "Hypothesis": {"type": "string"},
                    "Metrics": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["Name", "Description", "Hypothesis", "Metrics"]
            },
            "minItems": 5,
            "maxItems": 5
        }
    },
    "required": ["Experiments"]
}



experiments_scoring_prompt_template = """
You are an expert in evaluating business experiments. Based on the provided experiments, score each experiment on the following criteria from 1 to 10:
- Impact: The expectation about the degree to which the idea will improve the metric being focused on.
- Confidence: How strongly you believe the idea will produce the expected impact. Confidence should be higher if the test is an iteration of a previously successful test.
- Ease: The measure of the time and resources needed to run the experiment.

Calculate the average score for each experiment based on these criteria.

Experiments:
{experiments}

Your response must be in the following JSON format:

{{
    "ScoredExperiments": [
        {{
            "Name": "Experiment 1",
            "Impact": 8,
            "Confidence": 7,
            "Ease": 6,
            "AverageScore": 7.0
        }},
        {{
            "Name": "Experiment 2",
            "Impact": 5,
            "Confidence": 9,
            "Ease": 4,
            "AverageScore": 6.0
        }},
        ...
    ]
}}
"""


experiments_scoring_guided_json = {
    "type": "object",
    "properties": {
        "ScoredExperiments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Name": {"type": "string"},
                    "Impact": {"type": "integer", "minimum": 1, "maximum": 10},
                    "Confidence": {"type": "integer", "minimum": 1, "maximum": 10},
                    "Ease": {"type": "integer", "minimum": 1, "maximum": 10},
                    "AverageScore": {"type": "number", "minimum": 1.0, "maximum": 10.0}
                },
                "required": ["Name", "Impact", "Confidence", "Ease", "AverageScore"]
            }
        }
    },
    "required": ["ScoredExperiments"]
}



planner_prompt_template = """
You are a planner. Your responsibility is to create a comprehensive plan to help your team answer a research question. 
Questions may vary from simple to complex, multi-step queries. Your plan should provide appropriate guidance for your 
team to use an internet search engine effectively.

Focus on highlighting the most relevant search term to start with, as another team member will use your suggestions 
to search for relevant information.

If you receive feedback, consider it to adjust your plan accordingly:
Feedback: {feedback}

Here are your previous plans:
{previous_plans}
Consider this information when creating your new plan.

Current date and time:
{datetime}

Your response must take the following json format:

    "search_term": "The most relevant search term to start with"
    "overall_strategy": "The overall strategy to guide the search process"
    "additional_information": "Any additional information to guide the search including other search terms or filters"

"""

planner_guided_json = {
    "type": "object",
    "properties": {
        "search_term": {
            "type": "string",
            "description": "The most relevant search term to start with"
        },
        "overall_strategy": {
            "type": "string",
            "description": "The overall strategy to guide the search process"
        },
        "additional_information": {
            "type": "string",
            "description": "Any additional information to guide the search including other search terms or filters"
        }
    },
    "required": ["search_term", "overall_strategy", "additional_information"]
}


researcher_prompt_template = """
You are a researcher. You will be presented with a search engine results page containing a list of potentially relevant 
search results. Your task is to read through these results, select the most relevant one, and provide a comprehensive 
reason for your selection.

here is the search engine results page:
{serp}

Return your findings in the following json format:

    "selected_page_url": "The exact URL of the page you selected",
    "description": "A brief description of the page",
    "reason_for_selection": "Why you selected this page"


Adjust your selection based on any feedback received:
Feedback: {feedback}

Here are your previous selections:
{previous_selections}
Consider this information when making your new selection.

Current date and time:
{datetime}
"""

researcher_guided_json = {
    "type": "object",
    "properties": {
        "selected_page_url": {
            "type": "string",
            "description": "The exact URL of the page you selected"
        },
        "description": {
            "type": "string",
            "description": "A brief description of the page"
        },
        "reason_for_selection": {
            "type": "string",
            "description": "Why you selected this page"
        }
    },
    "required": ["selected_page_url", "description", "reason_for_selection"]
}


reporter_prompt_template = """
You are a reporter. You will be presented with a webpage containing information relevant to the research question. 
Your task is to provide a comprehensive answer to the research question based on the information found on the page. 
Ensure to cite and reference your sources.

The research will be presented as a dictionary with the source as a URL and the content as the text on the page:
Research: {research}

Structure your response as follows:
Based on the information gathered, here is the comprehensive response to the query:
"The sky appears blue because of a phenomenon called Rayleigh scattering, which causes shorter wavelengths of 
light (blue) to scatter more than longer wavelengths (red) [1]. This scattering causes the sky to look blue most of 
the time [1]. Additionally, during sunrise and sunset, the sky can appear red or orange because the light has to 
pass through more atmosphere, scattering the shorter blue wavelengths out of the line of sight and allowing the 
longer red wavelengths to dominate [2]."

Sources:
[1] https://example.com/science/why-is-the-sky-blue
[2] https://example.com/science/sunrise-sunset-colors

Adjust your response based on any feedback received:
Feedback: {feedback}

Here are your previous reports:
{previous_reports}

Current date and time:
{datetime}
"""

reviewer_prompt_template = """

You are a reviewer. Your task is to review the reporter's response to the research question and provide feedback. 

Your feedback should include reasons for passing or failing the review and suggestions for improvement. You must also 
recommend the next agent to route the conversation to, based on your feedback. Choose one of the following: planner,
researcher, reporter, or final_report. If you pass the review, you MUST select "final_report".

Consider the previous agents' work and responsibilities:
Previous agents' work:
planner: {planner}
researcher: {researcher}
reporter: {reporter}

in general if you need to run different searches, you should route the conversation to the planner.
If you need to find a different source from the existing SERP, you should route the conversation to the researcher.
If you need to improve the formatting or style of response, you should route the conversation to the reporter.

here are the agents' responsibilities to guide you with routing and feedback:
Agents' responsibilities:
planner: {planner_responsibilities}
researcher: {researcher_responsibilities}
reporter: {reporter_responsibilities}

You should consider the SERP the researcher used, 
this might impact your decision on the next agent to route the conversation to and any feedback you present.
SERP: {serp}

You should consider the previous feedback you have given when providing new feedback.
Feedback: {feedback}

Current date and time:
{datetime}

You must present your feedback in the following json format:

    "feedback": "Your feedback here. Along with your feedback explain why you have passed it to the specific agent",
    "pass_review": "True/False",
    "comprehensive": "True/False",
    "citations_provided": "True/False",
    "relevant_to_research_question": "True/False",
    "suggest_next_agent": "one of the following: planner/researcher/reporter/final_report"

"""
reviewer_guided_json = {
    "type": "object",
    "properties": {
        "feedback": {
            "type": "string",
            "description": "Your feedback here. Along with your feedback explain why you have passed it to the specific agent"
        },
        "pass_review": {
            "type": "boolean",
            "description": "True/False"
        },
        "comprehensive": {
            "type": "boolean",
            "description": "True/False"
        },
        "citations_provided": {
            "type": "boolean",
            "description": "True/False"
        },
        "relevant_to_research_question": {
            "type": "boolean",
            "description": "True/False"
        },
        "suggest_next_agent": {
            "type": "string",
            "description": "one of the following: planner/researcher/reporter/final_report"
        }
    },
    "required": ["feedback", "pass_review", "comprehensive", "citations_provided", "relevant_to_research_question", "suggest_next_agent"]
}
