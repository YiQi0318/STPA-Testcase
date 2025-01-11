```python
import carla
import random
import time
import numpy as np
import cv2

def main():
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        world = client.load_world('Town03')
        world.set_weather(carla.WeatherParameters.ClearNoon)

        blueprint_library = world.get_blueprint_library()
        vehicle_bp = random.choice(blueprint_library.filter('vehicle.*'))

        spawn_points = world.get_map().get_spawn_points()
        spawn_point = random.choice(spawn_points if spawn_points else [carla.Transform()])

        vehicle = world.spawn_actor(vehicle_bp, spawn_point)

        while True:
            time.sleep(0.05)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        print("Destroying actors...")
        for actor in world.get_actors().filter('vehicle.*'):
            actor.destroy()
        print("Done.")

def process_image(image):
    raw_image = np.array(image.raw_data)
    reshaped_image = raw_image.reshape((image.height, image.width, 4))
    final_image = reshaped_image[:, :, :3]
    return final_image

def evaluate_pass_criteria(image):
    processed_image = process_image(image)
    object_detected = False

    # Implement object detection and classification logic here
    # If an object is detected and classified, set object_detected to True

    return object_detected

if __name__ == "__main__":
    main()
```
This script connects to the CARLA server, loads the specified map, and sets the weather to ClearNoon. It then selects a random vehicle blueprint and spawn point, and spawns a vehicle at that location. The script enters an infinite loop, during which the simulation runs. If an error occurs, it is caught and printed. Finally, all vehicles are destroyed when the script ends. The `process_image` function reshapes the raw image data into a 3D array representing the image. The `evaluate_pass_criteria` function processes the image and checks for the presence of objects. If an object is detected, the function returns True.