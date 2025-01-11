```python
import carla
import random
import time
import numpy as np
import cv2

def main():
    client = None
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        # Load map
        map_name = random.choice(['Town03', 'Town10'])
        world = client.load_world(map_name)

        # Set up the environment
        weather = carla.WeatherParameters.ClearNoon
        world.set_weather(weather)

        # Spawn vehicle
        vehicle_bp = random.choice(blueprint_library.filter('vehicle.*'))
        spawn_point = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)

        # Attach sensors
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        camera.listen(lambda image: process_image(image))

        # Run the simulation
        while True:
            world.wait_for_tick()

    except Exception as e:
        print(f"Exception occurred: {str(e)}")

    finally:
        if client is not None:
            print("Destroying actors...")
            for actor in world.get_actors().filter('vehicle.*'):
                actor.destroy()
            print("All actors destroyed.")

def process_image(image):
    # Convert image to numpy array
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array = array[:, :, ::-1]

    # Process image here
    # ...

if __name__ == '__main__':
    main()
```

This script connects to a CARLA server, loads a map, sets up the environment, spawns a vehicle with a camera sensor, and runs the simulation. It handles exceptions and ensures that all actors are destroyed at the end. The image processing function currently does nothing, as the pass criteria and specific image processing logic were not provided.