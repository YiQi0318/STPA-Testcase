```python
import carla
import random
import time
import numpy as np
import cv2

def main():
    try:
        # Connect to the CARLA server
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        # Load the Town03 map
        world = client.load_world('Town03')

        # Set the environment conditions
        weather = carla.WeatherParameters.ClearNoon
        world.set_weather(weather)

        # Get a random vehicle blueprint
        blueprint_library = world.get_blueprint_library()
        bp = random.choice(blueprint_library.filter('vehicle'))

        # Spawn the vehicle
        spawn_point = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(bp, spawn_point)

        # Attach the sensor to the vehicle
        bp = blueprint_library.find('sensor.camera.rgb')
        transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        sensor = world.spawn_actor(bp, transform, attach_to=vehicle)

        # Register the image processing function to the sensor's output
        sensor.listen(lambda image: process_image(image))

        # Run the simulation for a while
        time.sleep(20)

    finally:
        # Clean up and end the simulation
        sensor.destroy()
        vehicle.destroy()

def process_image(image):
    # Convert the image data to an array
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))

    # Convert the array to an image
    image = cv2.cvtColor(array, cv2.COLOR_RGBA2BGR)

    # Implement the pass criteria evaluation function here
    pass

if __name__ == '__main__':
    main()
```
This script connects to the CARLA server, loads the Town03 map, sets the weather to ClearNoon, spawns a vehicle with a sensor, and runs the simulation for a while. The sensor's output is processed by the `process_image` function, which currently does nothing. The pass criteria evaluation function is not implemented because the pass criteria is unknown. Finally, the script destroys the sensor and the vehicle to clean up.