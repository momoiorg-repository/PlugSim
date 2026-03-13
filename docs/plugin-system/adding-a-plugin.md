---
title: Adding a Plugin
parent: Plugin System
nav_order: 2
---

# Adding a Plugin
{: .no_toc }

<details open markdown="block">
  <summary>Table of contents</summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Option A — Scaffold with the CLI

The quickest way to get a valid plugin skeleton:

```bash
plugsim init
```

You will be prompted for:

```
Plugin type [world/robot/logic/app]: world
Plugin name: my_factory
Version [1.0.0]:
Description: My custom factory environment
ROS distro [jazzy]:
Isaac Sim constraint [>=5.0.0]:
```

This creates:

```
plugin/my_factory/
├── METADATA.yaml
├── README.md
└── assets/
```

Then edit `METADATA.yaml` and add your USD / Python / launch files.

---

## Option B — Manual

1. Create a directory directly under `plugin/`:

    ```bash
    mkdir -p plugin/my_factory/assets
    ```

2. Create `plugin/my_factory/METADATA.yaml`:

    ```yaml
    plugin_type: world
    name: my_factory
    version: 1.0.0
    description: "My custom factory environment"
    compatibility:
      isaac_sim: ">=5.0.0"
      ros_distro: jazzy
    entry_point:
      usd: assets/scene.usd
      app: app.py
    ```

3. Add your files (`app.py`, USD assets, launch files, etc.).

4. Verify discovery:

    ```bash
    plugsim scan
    ```

---

## File placement tips

| File type | Recommended location |
|-----------|----------------------|
| USD scene / robot assets | `assets/` |
| Isaac Sim standalone script | `app.py` at plugin root |
| ROS 2 launch file | `launch/<name>.launch.py` |
| ROS 2 workspace | `<name>_ws/` |
| Config / parameter file | `config/params.yaml` |

All paths in `METADATA.yaml` are **relative to the plugin's own directory**. Inside the container they become `/plugin/<name>/<path>`.

---

## Testing your plugin

```bash
plugsim validate            # check compatibility before starting
plugsim up                  # start container
plugsim exec my_factory     # run the plugin
```

Use `plugsim info my_factory` to confirm the parsed metadata looks correct before running.

---

## Assets in a separate repository

If your USD assets are large, keep them in a separate git repository and document the clone step in your plugin's `README.md`:

```bash
git clone https://github.com/your-org/my_factory_assets.git \
    plugin/my_factory/assets
```

Add `plugin/my_factory/assets/` to the root `.gitignore` of this repository so the asset repo is not accidentally committed as an embedded repo.
