# background_identifier.py

import json
import os
from states.state import AgentGraphState

def match_industry(state: AgentGraphState, profile_file: str, business_data_file: str):
    # Load the profile and business data from the given JSON files
    with open(profile_file, 'r') as f:
        profile_data = json.load(f)
        
    with open(business_data_file, 'r') as f:
        business_data = json.load(f)
    
    # Extract the industry from the profile
    profile_industry = profile_data.get("Industry", "").lower()
    
    # Search for the industry in the business data
    matching_data = []
    for industry in business_data:
        if industry.get("Industry Name", "").lower() == profile_industry:
            matching_data.append(industry)
    
    # Create a response message
    if matching_data:
        content = f"Found matching industry data for {profile_industry.capitalize()} industry."
    else:
        content = f"No matching industry data found for {profile_industry.capitalize()} industry."
    
    # Update the state with the matching data or an empty list, ensuring to follow the required message format
    state["checker_response"] = [{
        "role": "system",
        "content": json.dumps({
            "message": content,
            "data": matching_data
        })
    }]
    
    print(f"match_industry: {content}")
    return state
