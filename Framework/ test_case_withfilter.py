import os
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

api_key = os.getenv('OPENAI_API_KEY', '[Your Key]')
client = OpenAI(api_key=api_key)

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

def read_test_scenarios(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    test_scenarios = []
    current_scenario = {}
    current_key = None

    for line in lines:
        line = line.strip()
        if ":" in line:
            key_part, value_part = line.split(':', 1)
            current_key = key_part.strip()
            current_scenario[current_key] = value_part.strip()
        elif line == "":
            if current_scenario:
                test_scenarios.append(current_scenario)
                current_scenario = {}
                current_key = None
        elif current_key:
            if current_key in current_scenario:
                current_scenario[current_key] += " " + line
            else:
                current_scenario[current_key] = line

    if current_scenario:
        test_scenarios.append(current_scenario)

    return test_scenarios

def are_test_cases_similar(test_case1, test_case2, threshold=0.85):
    """ Check if two test cases are similar using cosine similarity. """
    vectorizer = TfidfVectorizer().fit_transform([test_case1, test_case2])
    vectors = vectorizer.toarray()
    similarity = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return similarity > threshold

def generate_formatted_test_cases(scenarios):
    formatted_test_cases = []

    for index, scenario in enumerate(scenarios, start=1):
        # Constructing the prompt to be specific about the output format
        prompt = f"Generate a formatted test case description based on the provided data:\n"
        prompt += f"Scenery: {scenario.get('Scenery', 'Urban area: intersections (Town03)')}\n"
        prompt += f"Environment: {scenario.get('Environment', 'Weather and Visibility (1- ClearNoon)')}\n"
        prompt += f"Dynamic elements: {scenario.get('Dynamic elements', 'Pedestrians, Vehicles types (Car), Vehicles control (Throttle)')}\n"
        prompt += f"Context: {scenario.get('Context', 'Obstacle (Position and Amount), Sensor type (RGB camera), Sensor feed delay time (immediate)')}\n"
        prompt += f"Pass criteria: {scenario.get('Pass criteria', 'PC1: Model accurately detect and classify objects (acc>90%) despite potential misleading features.')}\n\n"
        prompt += "Format this data as follows:\n"
        prompt += f"Test case {index}:\n"
        prompt += "Scenery: [detailed scenery description]\n"
        prompt += "Environment: [detailed environment conditions]\n"
        prompt += "Dynamic elements: [details about dynamic elements involved]\n"
        prompt += "Context: [specific context details]\n"
        prompt += "Pass criteria: [detailed pass criteria]\n"

        # Generate the test case
        formatted_description = call_gpt4(prompt, max_tokens=1024, temperature=0.5)

        # Check for similarity with existing test cases
        is_similar = False
        for existing_test_case in formatted_test_cases:
            if are_test_cases_similar(formatted_description, existing_test_case):
                print(f"Skipping similar scenario at index {index} (Semantic Check)")
                is_similar = True
                break

        # Add to the list if not similar
        if not is_similar:
            formatted_test_cases.append(formatted_description)

    return formatted_test_cases

def save_to_file(content, file_name):
    with open(file_name, 'w') as file:
        file.write("\n\n".join(content))

def generate_carla_code(test_case, model="text-davinci-002"):
    # Detailed and specific prompt asking for a complete CARLA simulation code
    prompt = f"""
    Generate a complete Python script for a CARLA simulator based on the following test case:

{test_case}

The script must:
1. Import all necessary Python packages, including `carla`, `random`, `time`, `numpy`, and `opencv-python` (`cv2`).
2. Connect to the CARLA server at 'localhost' on port 2000 and handle any connection errors.
3. Load a random map from the list ['Town03', 'Town10'].
4. Set up synchronous mode and fixed time steps for simulation precision.
5. Spawn a vehicle with autopilot enabled.
6. Attach an RGB camera sensor to the vehicle and configure it with appropriate attributes.
7. Implement an image processing function using OpenCV that processes the captured images and displays them.
8. Ensure the code handles image processing correctly without placeholders or incomplete logic.
9. Include a pass criteria evaluation function with real logic for detecting and classifying objects in the images.
10. Ensure proper cleanup by destroying all actors (vehicles, sensors, etc.) at the end of the simulation.
11. Output only the plain Python code, without any markdown formatting, explanations, or additional text. Ensure there are no markdown code blocks or introductory/explanatory comments.

The script should be fully executable and should not require any additional implementation for core functionalities.
"""

    result = call_gpt4(prompt, max_tokens=1500, temperature=0.5)  # Increased max_tokens for more detailed output
    return result


# Paths to your files
scenario_file_path = "bbw_test_scenarios.txt"
test_cases_file_path = "bbw_vehicles_test_cases_with.txt"
carla_code_file_path = "bbw_carla_simulation_with.py"

# Processing test scenarios
scenarios = read_test_scenarios(scenario_file_path)
test_cases = generate_formatted_test_cases(scenarios)
save_to_file(test_cases, test_cases_file_path)

# Generate CARLA simulation code for the first test case
carla_code = generate_carla_code(test_cases[0])
save_to_file([carla_code], carla_code_file_path)
