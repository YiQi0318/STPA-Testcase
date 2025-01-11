import difflib
import os

def load_code(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def extract_map_selection(code):
    map_lines = []
    for line in code.splitlines():
        if 'load_world' in line or 'Town' in line:
            map_lines.append(line)
    return '\n'.join(map_lines)

def extract_weather_setting(code):
    weather_lines = []
    for line in code.splitlines():
        if 'set_weather' in line or 'WeatherParameters' in line:
            weather_lines.append(line)
    return '\n'.join(weather_lines)

def extract_dynamic_elements(code):
    dynamic_lines = []
    for line in code.splitlines():
        if 'Brake-by-Wire' in line or 'BBW' in line or 'simulate_distraction' in line or 'spawn_vehicle' in line or 'world.spawn_actor' in line:
            dynamic_lines.append(line)
    return '\n'.join(dynamic_lines)

def compare_sections(code1, code2):
    map_similarity = difflib.SequenceMatcher(None, extract_map_selection(code1), extract_map_selection(code2)).ratio()
    weather_similarity = difflib.SequenceMatcher(None, extract_weather_setting(code1), extract_weather_setting(code2)).ratio()
    dynamic_similarity = difflib.SequenceMatcher(None, extract_dynamic_elements(code1), extract_dynamic_elements(code2)).ratio()
    
    return map_similarity, weather_similarity, dynamic_similarity

def compare_with_baseline(baseline_path, generated_code_root):
    baseline_code = load_code(baseline_path)
    
    results = []

    for dirpath, _, filenames in os.walk(generated_code_root):
        for filename in filenames:
            if filename.endswith('.py'):  # Assuming the code files are Python files
                generated_code_path = os.path.join(dirpath, filename)
                generated_code = load_code(generated_code_path)
                
                map_similarity, weather_similarity, dynamic_similarity = compare_sections(baseline_code, generated_code)
                
                results.append({
                    "filename": filename,
                    "map_similarity": map_similarity,
                    "weather_similarity": weather_similarity,
                    "dynamic_similarity": dynamic_similarity
                })
    
    return results

def main():
    baseline_path = "bbw_carla_baseline.py"  # Replace with your baseline code path
    generated_code_root = "bbw_carla_simulation_cases/"  # Replace with the root directory of generated codes
    
    comparison_results = compare_with_baseline(baseline_path, generated_code_root)
    
    for result in comparison_results:
        print(f"File: {result['filename']}")
        print(f"  Map Selection Similarity: {result['map_similarity']:.2f}")
        print(f"  Weather Setting Similarity: {result['weather_similarity']:.2f}")
        print(f"  Dynamic Elements Similarity: {result['dynamic_similarity']:.2f}")
        print("-" * 40)

if __name__ == "__main__":
    main()
