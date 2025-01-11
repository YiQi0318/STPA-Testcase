import os
from openai import OpenAI
import re
from time import sleep

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY', '[Your Key]]')
client = OpenAI(api_key=api_key)

# Template structure
test_scenario_template = """
Test Scenario:
Scenery: {scenery_details}
Environment: {environment_details}
Dynamic elements: {dynamic_elements_details}
Context: {context_details}
Pass criteria: {pass_criteria}
"""

class UCA:
    def __init__(self, controller, ca_type, controlled_part, context, linked_hazards):
        self.controller = controller
        self.ca_type = ca_type
        self.controlled_part = controlled_part
        self.context = context
        self.linked_hazards = linked_hazards

def load_uca_from_file(filename):
    ucas = []
    current_uca = {}

    with open(filename, 'r') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()

        if line.startswith("UCA"):
            if current_uca:
                ucas.append(UCA(**current_uca))
            current_uca = {}
        elif line.startswith("Controller"):
            current_uca['controller'] = line.split(": ", 1)[1]
        elif line.startswith("CA Type"):
            current_uca['ca_type'] = line.split(": ", 1)[1]
        elif line.startswith("Controlled Part"):
            current_uca['controlled_part'] = line.split(": ", 1)[1]
        elif line.startswith("Context"):
            current_uca['context'] = line.split(": ", 1)[1]
        elif line.startswith("Linked Hazards"):
            hazards_str = line.split(": ", 1)[1]
            current_uca['linked_hazards'] = hazards_str.strip("[]").split(", ")

    if current_uca:
        ucas.append(UCA(**current_uca))

    return ucas

def call_gpt4(prompt, max_tokens=100, temperature=0.5):
    """ Helper function to call GPT-4 with basic error handling """

    response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
    return response.choices[0].message.content.strip()


def generate_scenery_via_gpt4(controller, ca_type, controlled_part, context):
    prompt = f"""
    Given the unsafe control action information:
    - Controller: '{controller}'
    - CA Type: '{ca_type}'
    - Controlled Part: '{controlled_part}'
    - Context: '{context}'
    
    Provide the scenery details in a test scenario format. Relate it to the CARLA simulator maps.

    Example:
    - S1: Urban areas, particularly focusing on complex traffic environments like intersections, highways, and areas with high pedestrian activity (mapping test scenarios to specific CARLA simulator maps: Town03 and Town10)
    - S2: Suburban areas, suitable for testing scenarios involving interactions with pedestrians, cyclists, and occasional vehicular traffic (Town01, Town02, and Town04)
    """
    result = call_gpt4(prompt, max_tokens=100, temperature=0.5)
    sleep(60)  # Add delay
    return result

def generate_environment_via_gpt4(controller, ca_type, controlled_part, context):
    prompt = f"""
    Given the unsafe control action information:
    - Controller: '{controller}'
    - CA Type: '{ca_type}'
    - Controlled Part: '{controlled_part}'
    - Context: '{context}'
    
    Provide the environment details (weather and visibility) in a test scenario format. Consider various weather and visibility conditions.

    Example:
    - Weather and Visibility (1-ClearNoon)
    - Weather and Visibility (4-WetCloudyNoon)
    - Weather and Visibility (8-ClearSunset)
    - Weather and Visibility (11-WetCloudySunset)
    """
    result = call_gpt4(prompt, max_tokens=100, temperature=0.5)
    sleep(60) 
    return result

def generate_dynamic_elements_via_gpt4(controller, ca_type, controlled_part, context):
    prompt = f"""
    Given the unsafe control action information:
    - Controller: '{controller}'
    - CA Type: '{ca_type}'
    - Controlled Part: '{controlled_part}'
    - Context: '{context}'
    
    Provide the dynamic elements details in a test scenario format. Consider the CARLA simulator.

    Example:
    - DE1: Pedestrians (CARLA allows getting a list of all pedestrians from the blueprint library and choose one)
    - DE2: Various types of vehicles (Car, Truck, Van, Motorcycle, and Bicycle)
    """
    result = call_gpt4(prompt, max_tokens=100, temperature=0.5)
    sleep(60) 
    return result

def generate_context_via_gpt4(controller, ca_type, controlled_part, context):
    prompt = f"""
    Given the unsafe control action information:
    - Controller: '{controller}'
    - CA Type: '{ca_type}'
    - Controlled Part: '{controlled_part}'
    - Context: '{context}'
    
    Provide the context details in a test scenario format. Include obstacles, sensors, and other relevant details.

    Example:
    - C1: Obstacle position: Various positions of static and dynamic obstacles
    - C2: Type of sensor feed: Different sensors like LiDAR, radar, and camera
    """
    result = call_gpt4(prompt, max_tokens=100, temperature=0.5)
    sleep(60) 
    return result

def generate_pass_criteria_via_gpt4(controller, ca_type, controlled_part, context, hazards):
    prompt = f"""
    Given the unsafe control action information:
    - Controller: '{controller}'
    - CA Type: '{ca_type}'
    - Controlled Part: '{controlled_part}'
    - Context: '{context}'
    - Linked Hazards: {hazards}
    
    The pass criteria based on the following questions:
    1. What could trigger the incorrect decisions of CA?
    2. How could correct decisions on CA become unsafe?

    Provide the clear pass criteria for a test scenario based on the answers to these questions.
    """
    result = call_gpt4(prompt, max_tokens=150, temperature=0.5)
    sleep(60) 
    return result

def generate_test_scenario(uca):
    """ Generate a single test scenario for each UCA """


    scenery_details = generate_scenery_via_gpt4(uca.controller, uca.ca_type, uca.controlled_part, uca.context)
    environment_details = generate_environment_via_gpt4(uca.controller, uca.ca_type, uca.controlled_part, uca.context)
    dynamic_elements_details = generate_dynamic_elements_via_gpt4(uca.controller, uca.ca_type, uca.controlled_part, uca.context)
    context_details = generate_context_via_gpt4(uca.controller, uca.ca_type, uca.controlled_part, uca.context)

    if '&' in context_details:
        context_main, context_explanation = context_details.split('&', 1)
    else:
        context_main = context_details
        context_explanation = "Further explanation not available."

    pass_criteria = generate_pass_criteria_via_gpt4(uca.controller, uca.ca_type, uca.controlled_part, uca.context, uca.linked_hazards)

    return test_scenario_template.format(
        scenery_details=scenery_details,
        environment_details=environment_details,
        dynamic_elements_details=dynamic_elements_details,
        context_details=context_main,
        pass_criteria=pass_criteria
    )


def generate_test_scenarios(ucas):
    test_scenarios = []
    for uca in ucas:
        test_scenario = generate_test_scenario(uca)
        test_scenarios.append(test_scenario)

    return "\n\n".join(test_scenarios)

def save_test_scenarios_to_file(scenarios, filename):
    with open(filename, 'w') as file:
        file.write(scenarios)

if __name__ == "__main__":
    ucas_path = "[bbw_uca.txt]"
    output_path = "[bbw_test_scenarios.txt]"

    # Load UCAs
    ucas = load_uca_from_file(ucas_path)

    # Generate test scenarios
    test_scenarios = generate_test_scenarios(ucas)

    # Save to file
    save_test_scenarios_to_file(test_scenarios, output_path)

    print(f"\nTest scenarios output saved to {output_path}")
