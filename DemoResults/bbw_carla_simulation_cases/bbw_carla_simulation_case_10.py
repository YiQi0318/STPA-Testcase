```python
import carla
import random
import time
import numpy as np
import cv2

def process_img(image):
    i = np.array(image.raw_data)
    i2 = i.reshape((image.height, image.width, 4))
    i3 = i2[:, :, :3]
    cv2.imshow("", i3)
    cv2.waitKey(1)

try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)

    world = client.load_world('Town01')

    weather = carla.WeatherParameters(
        cloudiness=0.0,
        precipitation=0.0,
        sun_altitude_angle=70.0
    )
    world.set_weather(weather)

    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.filter('model3')[0]

    spawn_point = random.choice(world.get_map().get_spawn_points())
    vehicle = world.spawn_actor(vehicle_bp, spawn_point)

    cam_bp = blueprint_library.find('sensor.camera.rgb')
    cam_bp.set_attribute('image_size_x', '800')
    cam_bp.set_attribute('image_size_y', '800')
    cam_bp.set_attribute('fov', '110')
    spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))
    sensor = world.spawn_actor(cam_bp, spawn_point, attach_to=vehicle)

    sensor.listen(lambda data: process_img(data))

    time.sleep(20)

finally:
    print('Destroying actors')
    sensor.destroy()
    vehicle.destroy()
    print('Done')
```
This script connects to the CARLA server, sets up the environment, and attaches an RGB camera to a vehicle. The camera's feed is processed in real-time using the `process_img` function, which displays the feed using OpenCV. After 20 seconds, the script destroys the actors to clean up.