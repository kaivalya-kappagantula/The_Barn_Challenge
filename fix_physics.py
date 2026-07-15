import os
import glob

# Define the paths to your world files
world_paths = [
    "/mnt/Storage/barn_ws/src/jackal_helper/worlds/BARN/*.world",
    "/mnt/Storage/barn_ws/src/jackal_helper/worlds/DynaBARN/*.world"
]

physics_tag = """
    <physics name="1ms" type="ode">
      <max_step_size>0.02</max_step_size>
      <real_time_update_rate>50</real_time_update_rate>
    </physics>
"""

for path in world_paths:
    for file_path in glob.glob(path):
        with open(file_path, 'r') as f:
            content = f.read()

        # Only edit if the physics tag isn't already there
        if "<physics" not in content:
            # Inject right after <world name="default">
            new_content = content.replace('<world name="default">', '<world name="default">' + physics_tag)
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"Fixed: {os.path.basename(file_path)}")
        else:
            print(f"Skipped (Already fixed): {os.path.basename(file_path)}")
