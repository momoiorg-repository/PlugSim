"""
Standalone Isaac Sim script to open the factory_base.usd world in livestream mode.
This script loads the specified USD world and runs the simulation with livestream capabilities.
"""

import argparse
import sys

# 1. SETUP ARGUMENT PARSER
# We do this BEFORE importing SimulationApp so we can configure it based on flags
parser = argparse.ArgumentParser(description="Isaac Sim Factory Livestream")
parser.add_argument("--cloud", action="store_true", help="Enable cloud livestream settings")
parser.add_argument("--ip", type=str, default="127.0.0.1", help="Public endpoint IP address (used if --cloud is set)")

# Use parse_known_args to avoid errors with internal Isaac Sim arguments
args, unknown = parser.parse_known_args()

from isaacsim import SimulationApp

# Configuration for the simulation application in livestream mode
CONFIG = {
    "width": 1280,
    "height": 720,
    "window_width": 1920,
    "window_height": 1080,
    "headless": True,   # Required for livestream mode
    "hide_ui": False,   # Show the GUI
    "renderer": "RaytracedLighting",
    "display_options": 3286,  # Set display options to show default grid
}

# Add livestream args only if --cloud is specified
if args.cloud:
    # We use the IP provided in the arguments
    ip_address = args.ip
    CONFIG["extra_args"] = [
        "--/app/livestream/publicEndpointAddress=" + ip_address, 
        "--/app/livestream/port=49100"
    ]
    print(f"Cloud livestream enabled on IP: {ip_address}")

# Start the Isaac Sim application
simulation_app = SimulationApp(launch_config=CONFIG)

# Import necessary modules after SimulationApp is initialized
import carb
import omni
import omni.graph.core as og
import omni.graph.action
import omni.kit.test
from isaacsim.core.api import PhysicsContext
from isaacsim.core.utils.extensions import enable_extension
import omni.usd
import omni.timeline
from isaacsim.core.api import World
from isaacsim.core.prims import Articulation
from isaacsim.core.utils.stage import add_reference_to_stage
import numpy as np
import time

# Note that this is not the system level rclpy, but one compiled for omniverse
import rclpy
from rclpy.node import Node
from std_msgs.msg import Empty
from geometry_msgs.msg import Pose, Point, Quaternion


class FactoryROS2Controller(Node):
    """ROS2 controller for the factory Xform_02 object."""
    
    def __init__(self, world, stage):
        super().__init__("factory_controller")
        
        self.world = world
        self.stage = stage
        self.timeline = omni.timeline.get_timeline_interface()
        
        # Target object path
        self.target_path = "/World/quicktrun/Xform_02"
        
        # Define open and close positions
        self._close_position = np.array([-142.32, -155.53, 83.83])  # Default/close pose
        self._open_position = np.array([-142.32, -193.53, 83.83])   # Open target pose
        self._target_orientation = np.array([0.0, 0.0, 0.0, 1.0])  # quaternion [x, y, z, w]
        
        # Current state
        self._is_open = False
        self._current_position = self._close_position.copy()  # Current actual position
        self._target_position = self._close_position.copy()   # Target position to move towards
        
        # Animation settings
        self._animation_speed = 0.05  # Speed of movement (0.01 = very slow, 0.1 = fast)
        self._is_animating = False
        
        # Setup ROS2 subscribers for open/close control
        self.open_sub = self.create_subscription(
            Empty, 
            "cnc/open", 
            self.open_callback, 
            10
        )
        
        self.close_sub = self.create_subscription(
            Empty, 
            "cnc/close", 
            self.close_callback, 
            10
        )
        
        self.get_logger().info("Factory ROS2 controller initialized")
        self.get_logger().info(f"Controlling object: {self.target_path}")
        self.get_logger().info("Open/Close positions:")
        self.get_logger().info(f"  - Close: {self._close_position}")
        self.get_logger().info(f"  - Open:  {self._open_position}")
        self.get_logger().info("Subscribed to topics:")
        self.get_logger().info("  - factory/xform_02/open (std_msgs/Empty)")
        self.get_logger().info("  - factory/xform_02/close (std_msgs/Empty)")
        self.get_logger().info(f"Animation speed: {self._animation_speed} (0.01=slow, 0.1=fast)")
    
    def open_callback(self, msg):
        """Callback to open the Xform_02 object."""
        if self.world.is_playing():
            self._target_position = self._open_position.copy()
            self._is_open = True
            self._is_animating = True
            self.get_logger().info(f"Opening Xform_02 to position: {self._target_position}")
    
    def close_callback(self, msg):
        """Callback to close the Xform_02 object."""
        if self.world.is_playing():
            self._target_position = self._close_position.copy()
            self._is_open = False
            self._is_animating = True
            self.get_logger().info(f"Closing Xform_02 to position: {self._target_position}")
    
    def update_animation(self):
        """Update the smooth animation between current and target positions."""
        if self._is_animating:
            # Calculate distance to target
            distance = np.linalg.norm(self._target_position - self._current_position)
            
            if distance > 0.01:  # If not close enough to target
                # Move towards target position
                direction = (self._target_position - self._current_position) / distance
                move_distance = min(self._animation_speed, distance)
                self._current_position += direction * move_distance
            else:
                # Close enough to target, stop animating
                self._current_position = self._target_position.copy()
                self._is_animating = False
                state = "open" if self._is_open else "closed"
                self.get_logger().info(f"Xform_02 animation completed - now {state}")
    
    def apply_pose(self):
        """Apply the current pose to the target object."""
        try:
            # Update animation first
            self.update_animation()
            
            # Get the USD prim for the target object
            prim = self.stage.GetPrimAtPath(self.target_path)
            if prim and prim.IsValid():
                # Set position using current animated position
                from pxr import Gf
                position = Gf.Vec3d(*self._current_position)
                prim.GetAttribute("xformOp:translate").Set(position)
                
                # Skip orientation setting to avoid the type mismatch error
                # The object will keep its original orientation
                
        except Exception as e:
            self.get_logger().warn(f"Failed to apply pose to {self.target_path}: {e}")


def load_robot_with_action_graph(stage, robot_usd_path, robot_prim_path="/World/Robot"):
    """
    Load a robot USD file with action graph enabled.
    
    Args:
        stage: USD stage
        robot_usd_path: Path to the robot USD file
        robot_prim_path: Path where the robot will be placed in the stage
    
    Returns:
        articulation: The loaded robot articulation
    """
    try:
        print(f"Loading robot USD: {robot_usd_path}")
        
        # Add reference to stage using Isaac Sim utility
        add_reference_to_stage(usd_path=robot_usd_path, prim_path=robot_prim_path)
        print(f"Robot loaded at path: {robot_prim_path}")
        
        # Enable action graph if it exists
        try:
            # Look for action graph nodes in the robot USD
            action_graph_paths = []
            
            # Search for action graph nodes (common patterns)
            from pxr import Usd
            robot_prim = stage.GetPrimAtPath(robot_prim_path)
            if robot_prim and robot_prim.IsValid():
                for prim in Usd.PrimRange(robot_prim):
                    if prim.GetTypeName() == "OmniGraphNode":
                        action_graph_paths.append(prim.GetPath())
                        print(f"Found action graph node: {prim.GetPath()}")
                
                # If no action graph nodes found, try to find them by name patterns
                if not action_graph_paths:
                    for prim in Usd.PrimRange(robot_prim):
                        prim_name = prim.GetName()
                        if "action" in prim_name.lower() or "graph" in prim_name.lower():
                            action_graph_paths.append(prim.GetPath())
                            print(f"Found potential action graph node: {prim.GetPath()}")
                
                if action_graph_paths:
                    print(f"Found {len(action_graph_paths)} action graph nodes")
                    
                    # Enable the action graph
                    for graph_path in action_graph_paths:
                        try:
                            # Get the action graph node
                            graph_prim = stage.GetPrimAtPath(graph_path)
                            if graph_prim and graph_prim.IsValid():
                                # Enable the action graph
                                graph_prim.GetAttribute("omni:graph:enabled").Set(True)
                                print(f"Enabled action graph at: {graph_path}")
                        except Exception as e:
                            print(f"Warning: Could not enable action graph at {graph_path}: {e}")
                else:
                    print("No action graph nodes found in robot USD")
            else:
                print(f"Warning: Robot prim not found at {robot_prim_path}")
                
        except Exception as e:
            print(f"Warning: Could not process action graphs: {e}")
        
        # Try to create an articulation for the robot
        try:
            articulation = Articulation(robot_prim_path)
            print(f"Created articulation for robot at: {robot_prim_path}")
            return articulation
        except Exception as e:
            print(f"Warning: Could not create articulation: {e}")
            return None
        
    except Exception as e:
        print(f"Error loading robot USD: {e}")
        return None


def main():
    """Main function to load and run the factory USD world in livestream mode."""
    
    # Configure livestream settings
    simulation_app.set_setting("/app/window/drawMouse", True)
    
    # Enable Livestream extension
    print("Enabling livestream extension...")
    enable_extension("omni.services.livestream.nvcf")
    enable_extension("omni.kit.livestream.webrtc")
    enable_extension("isaacsim.ros2.bridge")
    enable_extension("omni.graph.window.action")
    
    simulation_app.update()


    # Path to the USD world file
    usd_path = "/plugin/example_factory_world/assets/factory_base.usd"
    
    print(f"Loading USD world: {usd_path}")
    
    try:
        # Open the USD stage
        omni.usd.get_context().open_stage(usd_path)
        print("USD world loaded successfully!")
        
        # Get the current stage
        stage = omni.usd.get_context().get_stage()
        if stage:
            print(f"Stage loaded: {stage.GetRootLayer().identifier}")
        else:
            print("Warning: Stage not loaded properly")
            
    except Exception as e:
        print(f"Error loading USD world: {e}")
        print("Please check if the file path is correct and the USD file exists.")
        return
    
    # Create a world instance for simulation
    world = World(stage_units_in_meters=1.0)
    
    # Load robot USD with action graph
    robot_usd_path = "/plugin/example_melon_ros2/assets/melon.usd"
    robot_articulation = load_robot_with_action_graph(stage, robot_usd_path, "/World/MelonRobot")
    
    if robot_articulation:
        print("Robot loaded successfully with action graph enabled")
        # Add the robot articulation to the world scene
        world.scene.add(robot_articulation)
        print("Robot articulation added to world scene")
    else:
        print("Warning: Failed to load robot USD")
    
    # Initialize ROS2
    print("Initializing ROS2...")
    rclpy.init()
    
    # Create ROS2 controller
    ros_controller = FactoryROS2Controller(world, stage)
    
    # Start the simulation
    print("Starting simulation in livestream mode...")
    world.reset()
    
    # Start timeline
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    
    # Main livestream simulation loop with ROS2 integration
    print("Livestream simulation running with ROS2 control. Press Ctrl+C to exit.")
    print("Connect to the livestream server to view the simulation.")
    print("ROS2 topics available:")
    print("  - factory/xform_02/open (std_msgs/Empty) - Open Xform_02")
    print("  - factory/xform_02/close (std_msgs/Empty) - Close Xform_02")
    
    reset_needed = False
    try:
        while simulation_app.is_running() and not simulation_app.is_exiting():
            # Step the world simulation
            world.step(render=True)
            
            # Process ROS2 messages
            rclpy.spin_once(ros_controller, timeout_sec=0.0)
            
            # Apply pose changes to the target object
            ros_controller.apply_pose()
            
            # Handle timeline reset if needed
            if world.is_stopped() and not reset_needed:
                reset_needed = True
            if world.is_playing():
                if reset_needed:
                    world.reset()
                    reset_needed = False
            
    except KeyboardInterrupt:
        print("\nLivestream simulation stopped by user.")
    except Exception as e:
        print(f"Livestream simulation error: {e}")
    finally:
        # Cleanup
        print("Shutting down livestream simulation...")
        timeline.stop()
        ros_controller.destroy_node()
        rclpy.shutdown()
        world.clear()
        simulation_app.close()

if __name__ == "__main__":
    main()
