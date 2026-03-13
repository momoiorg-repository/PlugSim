---
title: Examples
nav_order: 5
has_children: true
---

# Examples

PlugSim ships with two example plugins that demonstrate the two main plugin patterns.

| Plugin | Type | Entry point | Description |
|--------|------|-------------|-------------|
| [example_factory_world]({% link examples/factory-world.md %}) | `world` | `app.py` | Isaac Sim factory environment loaded via standalone Python script |
| [example_melon_ros2]({% link examples/melon-ros2.md %}) | `robot` | `ros2 launch` | Melon mobile manipulator with full ROS 2 bringup |

---

## Running the examples

```bash
plugsim up

# factory world (Isaac Sim standalone)
plugsim exec example_factory_world

# Melon robot (ROS 2 launch)
plugsim exec example_melon_ros2
```

Make sure to clone the asset repositories first — see [Getting Started]({% link getting-started.md %}#2-clone-plugin-assets).
