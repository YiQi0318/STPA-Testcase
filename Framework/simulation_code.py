import os
from openai import OpenAI

# Setup API client
api_key = os.getenv('OPENAI_API_KEY', '[Your key]')
client = OpenAI(api_key=api_key)

def call_gpt4(prompt, max_tokens=1500, temperature=0.5):
    """ Helper function to call GPT-4 with basic error handling """
    try:
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
    except Exception as e:
        print(f"Error generating code: {e}")
        return None

def read_test_cases(file_path):
    """ 
    Read test cases from the specified file and parse into dictionaries.
    
    Purpose:
    - Load the test cases from the file.
    - Parse the content into a dictionary format for easy access.

    Key Components:
    - File Reading: Opens and reads the content from the specified file path.
    - Parsing: Converts the content into a list of dictionaries where each test case is stored.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    # Split by double newlines to separate test cases
    raw_test_cases = content.split("\n\n")
    
    test_cases = []
    for raw_case in raw_test_cases:
        test_case = {}
        lines = raw_case.split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                test_case[key.strip()] = value.strip()
        test_cases.append(test_case)
    
    return test_cases

def generate_carla_code(test_case, index):
    """ 
    Generate CARLA simulation code based on the test case, ensuring differentiation.
    
    Purpose:
    - Generates an executable Python script for a CARLA simulation based on the provided test case.

    Key Components:
    - Prompt Construction: Builds a detailed prompt using test case details to guide the GPT-4 model in generating accurate simulation code.
    - GPT-4 API Call: Sends the constructed prompt to GPT-4 and retrieves the generated code.
    - Error Handling: Catches and reports any errors encountered during the API call.
    """
    prompt = f"""
    Generate a complete, executable Python script for the CARLA simulator based on the following test case:

    Test Case {index}:
    Scenery: {test_case.get('Scenery', 'Unknown')}
    Environment: {test_case.get('Environment', 'Unknown')}
    Dynamic Elements: {test_case.get('Dynamic elements', 'Unknown')}
    Context: {test_case.get('Context', 'Unknown')}
    Pass Criteria: {test_case.get('Pass criteria', 'Unknown')}

    The script must:
    1. Import all necessary Python packages, including `carla`, `random`, `time`, `numpy`, and `opencv-python` (`cv2`).
    2. Connect to the CARLA server at 'localhost' on port 2000 and handle any connection errors.
    3. Load the specific map `{test_case.get('Scenery', 'Town01')}`.
    4. Set up the environment with conditions like `{test_case.get('Environment', 'ClearNoon')}`.
    5. Spawn specific dynamic elements: {test_case.get('Dynamic elements', 'None')} and handle their behavior according to the scenario.
    6. Attach sensors like `{test_case.get('Context', 'None')}` to the vehicle and configure them appropriately.
    7. Implement specific logic in the image processing function to meet the pass criteria `{test_case.get('Pass criteria', 'None')}`.
    8. Ensure the code handles all these aspects correctly without placeholders or incomplete logic.
    9. Include a pass criteria evaluation function with logic for detecting and classifying objects in the images, and handle exceptions.
    10. Ensure proper cleanup by destroying all actors (vehicles, sensors, etc.) at the end of the simulation.
    11. Output only the plain Python code, without any markdown formatting, explanations, or additional text. Ensure there are no markdown code blocks or introductory/explanatory comments.
    
    And the script must include the following key functions for each script:

    1. Main Function (main):
       - Purpose: The main function is the entry point of the script. It initializes the CARLA client, sets up the simulation environment, runs the simulation loop, and ensures proper cleanup.
       - Key Components:
         - Client Connection: Establishes a connection to the CARLA server.
         - World and Environment Setup: Loads the world (map) and configures the environment (weather, time of day).
         - Vehicle and Actor Spawning: Spawns vehicles, pedestrians, and other actors in the simulation.
         - Simulation Loop: Runs the simulation, ticking the world and processing sensor data.
         - Cleanup: Ensures that all actors (vehicles, sensors, etc.) are destroyed at the end of the simulation.

    2. Image Processing Function (process_image):
       - Purpose: Handles the processing of images captured by camera sensors attached to vehicles. This could include tasks such as displaying the images, saving them to disk, or running object detection algorithms.
       - Key Components:
         - Image Conversion: Converts raw image data from the sensor into a format suitable for processing (e.g., converting to a NumPy array).
         - Display or Save: Displays the image using OpenCV or saves it for later analysis.
         - Analysis: Runs any image analysis, such as detecting objects or evaluating the scene based on certain criteria.

    3. Pass Criteria Evaluation Function (evaluate_pass_criteria):
       - Purpose: Evaluates whether the simulation meets specific pass criteria, such as correctly detecting objects, maintaining a certain speed, or avoiding obstacles.
       - Key Components:
         - Input Parameters: Takes data from the simulation (e.g., sensor data, vehicle states) as input.
         - Logic: Contains the logic for evaluating whether the criteria are met, such as checking if objects are detected within a certain confidence threshold.
         - Output: Returns a boolean value or a score indicating whether the criteria are met.

    4. Actor Management Functions:
       - Spawning Actors:
         - Purpose: Handles the spawning of vehicles, pedestrians, and other actors in the simulation.
         - Components: Randomly or specifically selects spawn points, actor types, and initial states.
       - Destroying Actors:
         - Purpose: Ensures that all actors are properly destroyed at the end of the simulation to avoid resource leaks.
         - Components: Iterates through all spawned actors and calls the destroy method on each.

    5. Sensor Setup Functions:
       - Purpose: Attaches sensors (e.g., cameras, LiDAR, radar) to vehicles and configures their settings.
       - Key Components:
         - Sensor Blueprints: Selects the appropriate sensor blueprints from the CARLA blueprint library.
         - Configuration: Sets attributes such as image resolution, field of view, and sensor position.
         - Listening: Starts listening to the sensor data and directs it to the appropriate processing function.

    6. Error Handling and Cleanup:
       - Purpose: Ensures that the simulation can gracefully handle errors (e.g., connection issues) and that resources are properly cleaned up.
       - Key Components:
         - Try-Except Blocks: Wraps critical sections of code to catch and handle exceptions.
         - Finally Block: Ensures that all actors and resources are cleaned up even if an error occurs.
    The script should be fully executable and should not require any additional implementation for core functionalities.
    """

    result = call_gpt4(prompt, max_tokens=1500, temperature=0.5)
    if result is None:
        print("Failed to generate CARLA code.")
        return None
    return result

def save_to_file(content, file_name):
    """ 
    Save the generated content to a file.
    
    Purpose:
    - Stores the generated CARLA simulation script to a specified file path.

    Key Components:
    - File Writing: Opens a file for writing and saves the content.
    - Error Handling: Basic error handling to ensure the file is saved properly.
    """
    with open(file_name, 'w') as file:
        file.write(content)

# Paths to your files
test_cases_file_path = "bbw_vehicles_test_cases.txt"

# Read test cases from file
test_cases = read_test_cases(test_cases_file_path)

# Generate and save CARLA simulation code for each test case
for index, test_case in enumerate(test_cases, start=1):
    carla_code = generate_carla_code(test_case, index)
    if carla_code:
        carla_code_file_path = f"/LOCAL2/yiqi/bbw_carla_simulation_case_{index}.py"
        save_to_file(carla_code, carla_code_file_path)
        print(f"Generated and saved CARLA simulation code for Test Case {index}")
    else:
        print(f"Skipping Test Case {index} due to generation failure.")
