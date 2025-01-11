import os
import re
from openai import OpenAI

# Initialize the OpenAI client
api_key = os.getenv('OPENAI_API_KEY', '[Your OpenAI API Key]]')
client = OpenAI(api_key=api_key)

# Fixed CA types
ca_types = ['provides', 'not provides', 'too early', 'too late', 'stopped too soon', 'applied too long']

class Hazard:
    def __init__(self, id, description):
        self.id = id
        self.description = description

class ControlAction:
    def __init__(self, id, description, controller, controlled_part):
        self.id = id
        self.description = description
        self.controller = controller
        self.controlled_part = controlled_part

class UCA:
    def __init__(self, controller, ca_type, controlled_part, context, linked_hazards):
        self.controller = controller
        self.ca_type = ca_type
        self.controlled_part = controlled_part
        self.context = context
        self.linked_hazards = linked_hazards

def load_control_actions(file_path):
    control_actions = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        ca_id = None
        ca_description = ""
        controller = ""
        controlled_part = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("control actions: ca"):
                if ca_id is not None:
                    control_actions.append(ControlAction(ca_id, ca_description, controller, controlled_part))
                ca_id = line.split()[2]
                ca_description = ""
                controller = ""
                controlled_part = ""
            elif line.lower().startswith("from"):
                controller = line.split("From ", 1)[1]
            elif line.lower().startswith("to"):
                controlled_part = line.split("To ", 1)[1]
            else:
                ca_description = line

        # Add the last control action if any
        if ca_id is not None:
            control_actions.append(ControlAction(ca_id, ca_description, controller, controlled_part))

    return control_actions

def load_hazards(file_path):
    hazards = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if ":" in line:
                hazard_id, hazard_desc = line.split(":", 1)
                hazards.append(Hazard(hazard_id.strip(), hazard_desc.strip()))
    return hazards

def get_context_via_gpt4(controller, ca_type, controlled_part, ca_description):
    prompt = f"""
    Given the controller '{controller}', control action type '{ca_type}', and controlled part '{controlled_part}', provide a context for the unsafe control action in the Systems-Theoretic Process Analysis (STPA) method. Ensure the context is realistic and relevant.
    It is important to clarify that this content in a particular context and worst-case environment, will lead to a hazard，not the loss scenarios. Use the content after the given ‘{ca_description}’ as the control action, analysing the context in which UCA occurs based on this.
    Please list a variety of potential contexts, aiming to provide more than one.
    
    For example:
    Controller: Safety Driver
    CA Type: not provides
    Controlled Part: Brake-by-Wire(BBW)
    Context: 1. [when the vehicle is traveling at high speed on a highway.]
             2. [When the vehicle is in heavy traffic or in a busy urban environment.]
    
    Format:
    when [context]
    """
    #### due to [context]  It is important to clarify that this content pertains to the scenario or environment where the unsafe control action originated, rather than the situation in which the control action was carried out.
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
        max_tokens=200,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def link_to_hazards_via_gpt4(controller, ca_type, controlled_part, context, hazards):
    prompt = f"""
    Here are the list of hazards:
    {', '.join([f"{hazard.id}: {hazard.description}" for hazard in hazards])}
    
    Based on the controller '{controller}', control action type '{ca_type}', controlled part '{controlled_part}', and context '{context}', list the hazard identifiers that could be linked to the action.
    
    Format:
    [H1, H2, H3]
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def generate_unsafe_control_actions(control_actions, hazards):
    ucas = []
    for ca in control_actions:
        for ca_type in ca_types:
            context = get_context_via_gpt4(ca.controller, ca_type, ca.controlled_part, ca.description)
            linked_hazards = link_to_hazards_via_gpt4(ca.controller, ca_type, ca.controlled_part, context, hazards)
            ucas.append(UCA(ca.controller, ca_type, ca.controlled_part, context, linked_hazards))
    return ucas

def save_uca_to_file(ucas, filename):
    with open(filename, 'w') as file:
        file.write("Unsafe Control Actions (UCAs):\n")
        for index, uca in enumerate(ucas, start=1):
            file.write(f"UCA{index}:\n")
            file.write(f"  Controller: {uca.controller}\n")
            file.write(f"  CA Type: {uca.ca_type}\n")
            file.write(f"  Controlled Part: {uca.controlled_part}\n")
            file.write(f"  Context: {uca.context}\n")
            file.write(f"  Linked Hazards: {uca.linked_hazards}\n\n")

if __name__ == "__main__":
    # File paths (example paths, update with actual paths)
    control_actions_path = "[bbw_ca.txt]"
    hazards_path = "[brake_by_wire_system_of_automotive_vehicles_accidents_and_hazards.txt]"

    # Load control actions
    control_actions = load_control_actions(control_actions_path)
    
    # Debug print to verify loaded data
    print("Loaded Control Actions:")
    for ca in control_actions:
        print(f"ID: {ca.id}, Description: {ca.description}, Controller: {ca.controller}, Controlled Part: {ca.controlled_part}")

    # Load hazards
    hazards = load_hazards(hazards_path)

    # Generate UCAs
    ucas = generate_unsafe_control_actions(control_actions, hazards)

    # Example print to check UCAs
    print("Generated UCAs:", ucas)

    # Save UCAs to file
    ucas_filename = "bbw_full_vehicles_unsafe_control_actions.txt"
    save_uca_to_file(ucas, ucas_filename)

    print(f"\nUnsafe Control Actions (UCAs) output saved to {ucas_filename}")
