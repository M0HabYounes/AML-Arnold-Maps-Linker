# AML (Arnold Maps Linker)

Automate texture map linking in Maya's Arnold Renderer with ease! 
**AML** (Arnold Maps Linker) is a Python script designed to streamline texture workflows by automating the linking of texture maps. It’s flexible, adaptive, and fully customizable, making it a perfect tool for artists working with Maya and Arnold Renderer.

---

## Features

- **Automatic Texture Linking**: Select a **BaseColor map**, and AML links all related textures automatically.
- **Name Manager with UI**: Add, edit, or manage naming conventions directly through an intuitive user interface. No need to manually edit JSON files.
  - **Features of the TextureName Manager UI**:
    - Add Texture Name
    - Delete Texture Name
    - Toggle "Prefer EXR" for displacement maps
    - Enable or disable UDIM workflow support
- **Supported Texture Maps**: Automatically links the following texture maps:
  - BaseColor
  - Roughness
  - Normal
  - Metallic
  - Height
  - Opacity
- **Adjustment Nodes**:
  - Adds `aiColorCorrect` for BaseColor maps.
  - Adds `aiRange` for Roughness and Metallic maps for better control.
- **LOD Selection**: Automatically selects `LOD0` if texture maps have level-of-detail iterations.
- **UDIM Workflow Support**: Designed to handle high-resolution texture setups effortlessly.
- **Python Compatibility**: Works with Python **2.7 and above**, making it compatible with Maya **2017 and newer**.
- **Open Source**: Free to use, modify, and extend.

---

## Installation

1. **Download or Clone the Repository**:

   ```bash
   git clone https://github.com/M0HabYounes/AML-Arnold-Maps-Linker
   ```

2. **Copy Files to Maya's Scripts Directory**:

   - Copy the **AML/** folder and the `userSetup.py` file to your Maya `scripts` directory:
     - **Windows**: `Documents\maya\<version>\scripts`
     - **Mac**: `~/Library/Preferences/Autodesk/maya/<version>/scripts`
     - **Linux**: `~/maya/<version>/scripts`

3. **Restart Maya**:

   - AML will automatically load when Maya starts, thanks to `userSetup.py`.

   If you already have a `userSetup.py` file in your `scripts` directory, simply add the following lines to it:

   ```python
    import maya.cmds as cmds
    from AML_Tools import AML_Menu
  
    cmds.evalDeferred("from AML_Tools import AML_Menu; AML_Menu.run()")
   ```

---

## Usage

When you open the Texture Name Manager UI or attempt to link a texture, AML will prompt you to import a JSON file (e.g., `Texture_Maps`). This file contains texture naming conventions and will be saved for future sessions. You won’t need to re-import it every time you reload Maya.

The JSON file is included in the `AML_Tools/` folder located in your Maya scripts directory:

- **Path**: `Documents/maya/<version>/scripts/AML/`.

1. **Run AML**:

   - You will find an **AML Menu** in the Maya interface.
   - Select the Texture Name Manager from the menu to start managing your naming conventions.

2. **Add Naming Variations**:

   - Start adding reasonable variations of naming conventions for BaseColor, Roughness, and other supported maps. For example:
     - BaseColor: `Color`, `BaseColorMap`
     - Normal: `Bump`, `NormalMap`

3. **Assign Textures in Hypershade**:

   - Open the Hypershade editor.
   - Assign a new `aiStandardSurface` material.
   - Click & Hold Right-click the `aiStandardSurface` node and select **(AML) Link Texture**, or access the same option from the AML Menu.

4. **Enable UDIM and EXR Options**:

   - If your workflow uses UDIMs, toggle the UDIM option in the UI.
   - Prefer EXR for displacement? Toggle that option as well.

5. **Enjoy Streamlined Workflows**:

   - Let AML handle all the tedious texture linking for you!

---

## Example JSON Configuration

AML uses a JSON file to manage naming conventions for texture maps. The Name Manager UI syncs directly with this file, allowing you to update it without manual edits.

Here’s an example JSON configuration:

```json
{
  "BaseColor": [
    {"name": "BaseColor", "locked": true},
    {"name": "Diffuse", "locked": false}
  ],
  "Normal": [
    {"name": "Normal", "locked": true},
    {"name": "Bump", "locked": false}
  ],
  "udim": true,
  "prefer_exr": true
}
```

---

## Advanced Features

- **LOD Iterations**:
  - If texture maps include level-of-detail (LOD) iterations, AML automatically selects `LOD0` for optimal quality.
- **Adjustment Nodes**:
  - BaseColor: Adds `aiColorCorrect` for fine-tuning.
  - Roughness/Metallic: Adds `aiRange` for better control over the material’s response.
- **Name Manager UI**:
  - Add or delete texture names for BaseColor, Roughness, Normal, and other maps.
  - Toggle "Prefer EXR" for displacement maps.
  - Enable or disable UDIM workflows directly through the UI.

---

## Frequently Asked Questions (FAQ)

### 1. **What Maya versions are supported?**

AML is compatible with Maya **2017 and newer**. It works with both Python 2.7 and Python 3+.

### 2. **Do I need to manually edit the JSON file for naming conventions?**

No, AML includes a Name Manager UI that allows you to easily add, edit, or delete texture naming conventions without manually editing the JSON file.

### 3. **How does AML handle LODs (Level of Detail)?**

If a texture map has LOD iterations, AML will automatically select `LOD0` for optimal quality.

### 4. **Can I use AML for non-Arnold workflows?**

Currently, AML is designed specifically for Maya's Arnold Renderer. Future updates may include support for other renderers like Redshift or V-Ray.

### 5. **What happens if I don't enable UDIM workflow?**

If UDIM workflow is disabled, AML sets the `uvTilingMode` attribute of texture nodes to 0 for standard workflows.

### 6. **How do I reset the JSON file to default settings?**

Simply delete or replace the existing JSON file in the scripts folder. AML will prompt you to create or load a new one when launched.

---

## Future Plans / Features

- **Multi-Renderer Support**:
  - Expand compatibility to include Redshift, V-Ray, Blender, and Unreal Engine.
- **Batch Processing**:
  - Add support for linking textures across multiple materials in one go.
- **Improved UI**:
  - Add a progress bar and batch-editing capabilities in the Name Manager.
- **Extended Map Support**:
  - Include additional texture maps like Specular and Emissive.
- **Preset Systems**:
  - Enable users to save and load presets for texture linking workflows.

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## Contributions

Contributions are welcome! Feel free to fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you’d like to change.

---

## Contact

Developed by **Mohab Younes**.

- [LinkedIn](https://www.linkedin.com/in/mohab-younes/)
- [GitHub](https://github.com/M0HabYounes)

