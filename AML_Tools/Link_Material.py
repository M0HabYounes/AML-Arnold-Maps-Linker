"""
Arnold Maps Linker AML - v1.0.0
==========================
Automates the linking of texture maps in Maya based on JSON-based naming conventions.

Version: v1.0.0
Copyright (c) 2024 Mohab Younes
Licensed under the MIT License. See the LICENSE file for details.
"""

import maya.cmds as cmds
import os
import re
import json

# Save the JSON path using Maya's optionVar
def save_json_path(json_path):
    cmds.optionVar(sv=("json_file_path", json_path))

# Retrieve the saved JSON path
def get_saved_json_path():
    return cmds.optionVar(q="json_file_path") if cmds.optionVar(exists="json_file_path") else None

# Load texture names, using a persistent path or fallback
def load_texture_names():
    json_path = get_saved_json_path()

    # If a saved path exists, try to load the JSON
    if json_path:
        try:
            with open(json_path, 'r') as file:
                return json.load(file)
        except (IOError, ValueError):
            while True:
                # Prompt the user with an error dialog
                result = cmds.confirmDialog(
                    title="Error",
                    message="The saved JSON file could not be loaded. It might be missing, corrupted, or invalid.\n"
                            "Please select a valid JSON file to continue.",
                    button=["Select New File", "Cancel"],
                    defaultButton="Select New File",
                    cancelButton="Cancel",
                    dismissString="Cancel"
                )
                if result == "Cancel":
                    print("User canceled the operation.")
                    return  # Exit the function if the user cancels

                # Allow the user to select a new file
                json_path = cmds.fileDialog2(fileMode=1, caption="Select JSON File", fileFilter="JSON Files (*.json)")
                if json_path:
                    save_json_path(json_path[0])  # Save the new selected path
                    try:
                        with open(json_path[0], 'r') as file:
                            return json.load(file)  # Return loaded JSON data
                    except (IOError, ValueError):
                        # If the new file is also invalid, continue the loop
                        continue
                else:
                    # If no file is selected, loop again
                    continue
    else:
        # If no saved path exists, prompt the user to select a JSON file
        while True:
            result = cmds.confirmDialog(
                title="No File Selected",
                message="You must select a JSON file to continue.",
                button=["Select File", "Cancel"],
                defaultButton="Select File",
                cancelButton="Cancel",
                dismissString="Cancel"
            )

            if result == "Cancel":
                print("User canceled the operation.")
                return  # Exit the function if the user cancels

            json_path = cmds.fileDialog2(fileMode=1, caption="Select JSON File", fileFilter="JSON Files (*.json)")
            if json_path:
                save_json_path(json_path[0])  # Save the selected path
                try:
                    with open(json_path[0], 'r') as file:
                        return json.load(file)  # Return loaded JSON data
                except (IOError, ValueError):
                    cmds.confirmDialog(
                        title="Error",
                        message="The selected JSON file could not be loaded. It might be missing, corrupted, or invalid.\n"
                                "Please select a valid JSON file to continue.",
                        button=["OK"]
                    )
                    continue  # Prompt the user to select again
            else:
                # If no file is selected, continue prompting
                continue
# Fetch the common terms for roughness and base color from the JSON data
def open_file_dialog():
    # Open a file dialog to select a specific file (image)
    file_path = cmds.fileDialog2(fileMode=1, caption="Select BaseColor Image File", fileFilter="Image Files (*.tif *.png *.jpg *.jpeg *.bmp *.gif *.tga *.exr)")
    if file_path:
        return file_path[0]  # Return the selected file path
    return None

# Function to get the selected material (aiStandardSurface)
def get_selected_material():
    # Get the currently selected objects in the scene
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("No node selected. Please select a node first.")
        return None

    # Check if the selected object is an aiStandardSurface material
    materials = cmds.ls(l=True, type="aiStandardSurface", sl=True)
    material = materials[0]

    if not material:
        cmds.warning("No aiStandardSurface material found for the selected object.")
        return None

    return material

# Function to check if the file name contains keywords like "basecolor", "albedo", "diffuse" ,etc...
def validate_image_file(file_path, base_color_terms):

    # Get the base filename (case-insensitive)
    file_name = os.path.basename(file_path).lower()
    print("Validating file: {}".format(file_name))  # Debugging output

    # Add the default terms to check (case-insensitive)
    additional_terms = ["basecolor", "albedo", "diffuse"]
    all_terms = base_color_terms + additional_terms

    # Check if any of the combined terms are present in the filename
    for term in all_terms:
        if term.lower() in file_name:  # Case-insensitive substring match
            return True
    return False
def place_2d_texture(node_map, place2d_texture_node):
    # List of attributes to connect from the place2dTexture to the texture node
    connections = [
        'rotateUV', 'offset', 'noiseUV', 'vertexCameraOne', 'vertexUvThree', 'vertexUvTwo',
        'vertexUvOne', 'repeatUV', 'wrapV', 'wrapU', 'stagger', 'mirrorU', 'mirrorV',
        'rotateFrame', 'translateFrame', 'coverage'
    ]

    # Connect the place2dTexture node to the texture node
    cmds.connectAttr(place2d_texture_node + '.outUV', node_map + '.uvCoord')
    cmds.connectAttr(place2d_texture_node + '.outUvFilterSize', node_map + '.uvFilterSize')

    # Connect each additional attribute
    for i in connections:
        cmds.connectAttr(place2d_texture_node + '.' + i, node_map + '.' + i)

#TextureMaps Setup
def set_maya_bc_attributes(image_path, material, place2d_texture_node , udim):
    if not image_path or not material:
        cmds.warning("No valid image or material selected.")
        return

    # Create a texture node for the base color
    texture_node = cmds.shadingNode('file', asTexture=True, name='BaseColor_File')
    cmds.setAttr("{}.fileTextureName".format(texture_node), image_path, type="string")

    aicolorcorrect_node = cmds.shadingNode('aiColorCorrect', asShader=True, name='aiColorCorrect_Node')

    # Connect the texture's outColor to the baseColor of the material
    cmds.connectAttr("{}.outColor".format(texture_node), "{}.input".format(aicolorcorrect_node), f=True)

    cmds.connectAttr("{}.outColor".format(aicolorcorrect_node), "{}.baseColor".format(material), f=True)
    # Set the uvTilingMode attribute for the texture
    if not udim :
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 0)
    else:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 3)

    # Call place2dTexture to connect the place2dTexture node to the texture
    place_2d_texture(texture_node, place2d_texture_node)
def set_maya_roughness_attributes(image_path, material, place2d_texture_node, udim):
    if not image_path or not material:
        cmds.warning("No valid image or material selected.")
        return

    # Load the texture names from the JSON
    json_data = load_texture_names()
    if json_data is None:
        cmds.warning("No valid JSON data loaded.")
        return

    # Fetch the common terms for base color and roughness
    base_color_terms = [entry['name'] for entry in json_data.get("BaseColor", [])]
    roughness_terms = [entry['name'] for entry in json_data.get("Roughness", [])]

    if not base_color_terms or not roughness_terms:
        cmds.warning("No valid texture terms found in the JSON data.")
        return

    base_name, ext = os.path.splitext(image_path)

    # Remove the _LOD suffix from the base name
    base_name = re.sub(r'_LOD.*', '', base_name)
    image_path = base_name + ext

    found_valid_path = False
    roughness_path = None
    lod_levels = ["", "_LOD0", "_LOD1", "_LOD2"]  # Include LOD levels to check

    # Check if the image path contains any of the base color terms, and replace them with roughness-related terms
    for term in base_color_terms:
        for replacement in roughness_terms:
            match = re.search(r'{}'.format(re.escape(term)), image_path, re.IGNORECASE)
            if match:
                for lod in lod_levels:
                    # Replace the term and add LOD suffix if applicable
                    potential_roughness_path = (
                        image_path[:match.start()] + replacement + lod + image_path[match.end():]
                    )
                    potential_roughness_path = os.path.normpath(potential_roughness_path)

                    # Check if the file exists with the potential roughness path
                    image_extensions = ['.exr', '.jpg', '.png', '.tif', '.tiff']
                    for ext in image_extensions:
                        candidate_path = os.path.splitext(potential_roughness_path)[0] + ext
                        if os.path.exists(candidate_path):
                            roughness_path = candidate_path
                            found_valid_path = True
                            break

                    if found_valid_path:
                        break

            if found_valid_path:
                break
        if found_valid_path:
            break

    # If no valid roughness path is found, return
    if not found_valid_path:
        cmds.warning("No roughness texture found at path")
        return

    # Create the texture node for the roughness map
    texture_node = cmds.shadingNode('file', asTexture=True, name='Roughness_File')
    cmds.setAttr("{}.fileTextureName".format(texture_node), roughness_path, type="string")
    cmds.setAttr("{}.colorSpace".format(texture_node), "Raw", type="string")
    airange_node = cmds.shadingNode('aiRange', asShader=True, name='aiRange_Node')

    # Connect the texture's outAlpha to the roughness attribute of the material
    cmds.connectAttr("{}.outColor".format(texture_node), "{}.input".format(airange_node), f=True)
    cmds.connectAttr("{}.outColorR".format(airange_node), "{}.specularRoughness".format(material), f=True)

    # Set the uvTilingMode attribute for the texture node
    if not udim:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 0)
    else:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 3)

    # Call place2dTexture to connect the place2dTexture node to the texture
    place_2d_texture(texture_node, place2d_texture_node)
def set_maya_metallic_attributes(image_path, material, place2d_texture_node, udim):
    if not image_path or not material:
        cmds.warning("No valid image or material selected.")
        return

    # Load the texture names from the JSON
    json_data = load_texture_names()
    if json_data is None:
        cmds.warning("No valid JSON data loaded.")
        return

    # Fetch the common terms for base color and metallic from the JSON
    base_color_terms = [entry['name'] for entry in json_data.get("BaseColor", [])]
    metallic_terms = [entry['name'] for entry in json_data.get("Metallic", [])]

    if not base_color_terms or not metallic_terms:
        cmds.warning("No valid texture terms found in the JSON data.")
        return

    base_name, ext = os.path.splitext(image_path)

    # Remove the '_LOD' suffix from the base name if it exists
    base_name = re.sub(r'_LOD.*', '', base_name)
    image_path = base_name + ext

    found_valid_path = False
    metallic_path = None
    lod_levels = ["", "_LOD0", "_LOD1", "_LOD2"]  # Include LOD levels to check

    # Check if the image path contains any of the base color terms, and replace them with metallic-related terms
    for term in base_color_terms:
        for replacement in metallic_terms:
            match = re.search(r'{}'.format(re.escape(term)), image_path, re.IGNORECASE)
            if match:
                for lod in lod_levels:
                    # Replace the term and add LOD suffix if applicable
                    potential_metallic_path = (
                            image_path[:match.start()] + replacement + lod + image_path[match.end():]
                    )

                    # Check if the file exists with the potential metallic path
                    image_extensions = ['.exr', '.jpg', '.png', '.tif', '.tiff']
                    for ext in image_extensions:
                        candidate_path = os.path.splitext(potential_metallic_path)[0] + ext
                        if os.path.exists(candidate_path):
                            metallic_path = candidate_path
                            found_valid_path = True
                            break

                    if found_valid_path:
                        break

            if found_valid_path:
                break
        if found_valid_path:
            break

    # If no valid metallic path is found, return
    if not found_valid_path:
        cmds.warning("No metallic texture found at path")
        return

    # Create the texture node for the metallic map
    texture_node = cmds.shadingNode('file', asTexture=True, name='Metallic_File')
    cmds.setAttr("{}.fileTextureName".format(texture_node), metallic_path, type="string")
    cmds.setAttr("{}.colorSpace".format(texture_node), "Raw", type="string")
    airange_node = cmds.shadingNode('aiRange', asShader=True, name='aiRange_Node')

    # Connect the texture's outAlpha to the roughness attribute of the material
    cmds.connectAttr("{}.outColor".format(texture_node), "{}.input".format(airange_node), f=True)

    cmds.connectAttr("{}.outColorR".format(airange_node), "{}.metalness".format(material), f=True)

    if not udim:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 0)
    else:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 3)

        # Call place2dTexture to connect the place2dTexture node to the texture
    place_2d_texture(texture_node, place2d_texture_node)
def set_maya_displacement_attributes(image_path, material, place2d_texture_node, udim):
    if not image_path or not material:
        cmds.warning("No valid image or material selected.")
        return

    # Load the texture names from the JSON
    json_data = load_texture_names()
    if json_data is None:
        cmds.warning("No valid JSON data loaded.")
        return

    # Fetch the common terms for base color and displacement from the JSON
    base_color_terms = [entry['name'] for entry in json_data.get("BaseColor", [])]
    displacement_terms = [entry['name'] for entry in json_data.get("Height", [])]
    prefer_exr = json_data.get("prefer_exr")  # Default to False if not specified

    if not base_color_terms or not displacement_terms:
        cmds.warning("No valid texture terms found in the JSON data.")
        return

    base_name, ext = os.path.splitext(image_path)

    # Remove the '_LOD' suffix from the base name if it exists
    base_name = re.sub(r'_LOD.*', '', base_name)
    image_path = base_name + ext

    found_valid_path = False
    displacement_path = None
    lod_levels = ["", "_LOD0", "_LOD1", "_LOD2"]  # Include LOD levels to check

    # Check if the image path contains any of the base color terms, and replace them with  displacement-related terms
    for term in base_color_terms:
        for replacement in  displacement_terms:
            match = re.search(r'{}'.format(re.escape(term)), image_path, re.IGNORECASE)
            if match:
                for lod in lod_levels:
                    # Replace the term and add LOD suffix if applicable
                    potential_displacement_path = (
                            image_path[:match.start()] + replacement + lod + image_path[match.end():]
                    )

                    # Check if the file exists with the potential displacement path
                    image_extensions = ['.exr', '.jpg', '.png', '.tif', '.tiff']
                    if not prefer_exr:
                        image_extensions.remove('.exr')
                        image_extensions.append('.exr')

                    for ext in image_extensions:
                        candidate_path = os.path.splitext(potential_displacement_path)[0] + ext
                        if os.path.exists(candidate_path):
                            displacement_path = candidate_path
                            found_valid_path = True
                            break

                    if found_valid_path:
                        break

            if found_valid_path:
                break
        if found_valid_path:
            break

    # If no valid displacement path is found, return
    if not found_valid_path:
        cmds.warning("No displacement texture found at path")
        return

    # Create a texture node for the displacement map
    texture_node = cmds.shadingNode('file', asTexture=True, name='Displacement_File')
    cmds.setAttr("{}.fileTextureName".format(texture_node), displacement_path, type="string")
    cmds.setAttr("{}.colorSpace".format(texture_node), "Raw", type="string")

    # Create the displacementShader node
    displacement_map_node = cmds.shadingNode('displacementShader', asShader=True, name='DisplacementShader_Node')

    # Connect the texture node's outColorR to the displacementShader's displacement input
    cmds.connectAttr("{}.outColorR".format(texture_node), "{}.displacement".format(displacement_map_node), f=True)

    # Get the shading group connected to the material
    shading_group = cmds.listConnections(material, destination=True, source=False, type="shadingEngine")
    # Connect the displacementShader's displacement to the shading group's displacementShader input
    if shading_group:
        cmds.connectAttr("{}.displacement".format(displacement_map_node), "{}.displacementShader".format(shading_group[0]), f=True)

    # Set the uvTilingMode attribute for the texture node to a specific tiling mode
    if not udim:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 0)
    else:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 3)

        # Call place2dTexture to connect the place2dTexture node to the texture
    place_2d_texture(texture_node, place2d_texture_node)
def set_maya_normal_attributes(image_path, material, place2d_texture_node, udim):
    if not image_path or not material:
        cmds.warning("No valid image or material selected.")
        return

    # Load the texture names from the JSON
    json_data = load_texture_names()
    if json_data is None:
        cmds.warning("No valid JSON data loaded.")
        return

    # Fetch the common terms for base color and normal from the JSON
    base_color_terms = [entry['name'] for entry in json_data.get("BaseColor", [])]
    normal_terms = [entry['name'] for entry in json_data.get("Normal", [])]

    if not base_color_terms or not normal_terms:
        cmds.warning("No valid texture terms found in the JSON data.")
        return

    base_name, ext = os.path.splitext(image_path)

    # Remove the '_LOD' suffix from the base name if it exists
    base_name = re.sub(r'_LOD.*', '', base_name)
    image_path = base_name + ext

    found_valid_path = False
    normal_path = None
    lod_levels = ["", "_LOD0", "_LOD1", "_LOD2"]  # Include LOD levels to check

    # Check if the image path contains any of the base color terms, and replace them with normal-related terms
    for term in base_color_terms:
        for replacement in normal_terms:
            match = re.search(r'{}'.format(re.escape(term)), image_path, re.IGNORECASE)
            if match:
                for lod in lod_levels:
                    # Replace the term and add LOD suffix if applicable
                    potential_normal_path = (
                            image_path[:match.start()] + replacement + lod + image_path[match.end():]
                    )
                    # Check if the file exists with the potential normal path
                    image_extensions = ['.exr', '.jpg', '.png', '.tif', '.tiff']
                    for ext in image_extensions:
                        candidate_path = os.path.splitext(potential_normal_path)[0] + ext
                        if os.path.exists(candidate_path):
                            normal_path = candidate_path
                            found_valid_path = True
                            break

                    if found_valid_path:
                        break

            if found_valid_path:
                break
        if found_valid_path:
            break
    # If no valid normal path is found, return
    if not found_valid_path:
        cmds.warning("No normal texture found at path")
        return

    # Create a texture node for the normal map
    texture_node = cmds.shadingNode('file', asTexture=True, name='Normal_File')
    cmds.setAttr("{}.fileTextureName".format(texture_node), normal_path, type="string")
    cmds.setAttr("{}.colorSpace".format(texture_node), "Raw", type="string")

    # Create the aiNormalMap node
    normal_map_node = cmds.shadingNode('aiNormalMap', asShader=True, name='AiNormalMap_Node')

    # Connect the texture node's outColor to the aiNormalMap's normalCamera
    cmds.connectAttr("{}.outColor".format(texture_node), "{}.input".format(normal_map_node), f=True)

    # Connect the aiNormalMap's outNormal to the aiStandardSurface's normal input
    cmds.connectAttr("{}.outValue".format(normal_map_node), "{}.normalCamera".format(material), f=True)

    # Set the uvTilingMode attribute for the texture node
    if not udim:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 0)
    else:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 3)
        # Call place2dTexture to connect the place2dTexture node to the texture
    place_2d_texture(texture_node, place2d_texture_node)
def set_maya_opacity_attributes(image_path, material, place2d_texture_node, udim):
    if not image_path or not material:
        cmds.warning("No valid image or material selected.")
        return

    # Load the texture names from the JSON
    json_data = load_texture_names()
    if json_data is None:
        cmds.warning("No valid JSON data loaded.")
        return

    # Fetch the common terms for base color and opacity from the JSON
    base_color_terms = [entry['name'] for entry in json_data.get("BaseColor", [])]
    opacity_terms = [entry['name'] for entry in json_data.get("Opacity", [])]

    if not base_color_terms or not opacity_terms:
        cmds.warning("No valid texture terms found in the JSON data.")
        return

    base_name, ext = os.path.splitext(image_path)

    # Remove the '_LOD' suffix from the base name if it exists
    base_name = re.sub(r'_LOD.*', '', base_name)
    image_path = base_name + ext

    found_valid_path = False
    opacity_path = None
    lod_levels = ["", "_LOD0", "_LOD1", "_LOD2"]  # Include LOD levels to check

    # Check if the image path contains any of the base color terms, and replace them with opacity-related terms
    for term in base_color_terms:
        for replacement in  opacity_terms:
            match = re.search(r'{}'.format(re.escape(term)), image_path, re.IGNORECASE)
            if match:
                for lod in lod_levels:
                    # Replace the term and add LOD suffix if applicable
                    potential_opacity_path = (
                            image_path[:match.start()] + replacement + lod + image_path[match.end():]
                    )

                    # Check if the file exists with the potential opacity path
                    image_extensions = ['.exr', '.jpg', '.png', '.tif', '.tiff']
                    for ext in image_extensions:
                        candidate_path = os.path.splitext(potential_opacity_path)[0] + ext
                        if os.path.exists(candidate_path):
                            opacity_path = candidate_path
                            found_valid_path = True
                            break

                    if found_valid_path:
                        break

            if found_valid_path:
                break
        if found_valid_path:
            break

    # If no valid opacity path is found, return
    if not found_valid_path:
        cmds.warning("No opacity texture found at path")
        return

    # Create a texture node for the opacity map
    texture_node = cmds.shadingNode('file', asTexture=True, name='Opacity_File')
    cmds.setAttr("{}.fileTextureName".format(texture_node), opacity_path, type="string")
    cmds.setAttr("{}.colorSpace".format(texture_node), "Raw", type="string")

    cmds.connectAttr("{}.outColor".format(texture_node), "{}.opacity".format(material), f=True)

    # Set the uvTilingMode attribute for the texture node
    if not udim:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 0)
    else:
        cmds.setAttr("{}.uvTilingMode".format(texture_node), 3)

    # Set the ThinWalled To Checked

    cmds.setAttr("{}.thinWalled".format(material), 1)

    # Call place2dTexture to connect the place2dTexture node to the texture
    place_2d_texture(texture_node, place2d_texture_node)

# Main function to execute the script
def main():
    json_data = load_texture_names()
    if json_data is None:
        cmds.warning("No valid JSON data loaded.")
        return

    # Fetch the common terms for base color from the JSON
    udim_workflow = json_data.get("udim")  # Default to False if not specified

    base_color_terms = [entry['name'] for entry in json_data.get("BaseColor", [])]
    if not base_color_terms:
        cmds.warning("No Base Color terms found in the JSON data.")
        return
    # Open the file dialog to select the image file
    material = get_selected_material()

    if material:
        # Proceed only if an aiStandardSurface material is selected
        print("Selected aiStandardSurface material: {}".format(material))

        # Open file dialog to select an image
        file_path = open_file_dialog()

        if file_path:
            print("Selected file: {}".format(file_path))

            # Validate if the file name contains required keywords
            if not validate_image_file(file_path, base_color_terms):
                cmds.warning(
                    "The selected image file does not contain any related Basecolor Names in the filename. Please select the appropriate BaseColor map.")
            else:
                # Further processing here, like assigning the file to the material
                print("Valid BaseColor map selected.")

                # Create the place2dTexture node once
                place2d_texture_node = cmds.shadingNode("place2dTexture", name='Place2dTexture', asUtility=True)

                # Call your functions to set attributes and pass place2dTexture to each
                set_maya_bc_attributes(file_path, material, place2d_texture_node,udim_workflow)
                set_maya_metallic_attributes(file_path, material, place2d_texture_node,udim_workflow)
                set_maya_roughness_attributes(file_path, material, place2d_texture_node,udim_workflow)
                set_maya_opacity_attributes(file_path, material, place2d_texture_node,udim_workflow)
                set_maya_normal_attributes(file_path, material, place2d_texture_node,udim_workflow)
                set_maya_displacement_attributes(file_path, material, place2d_texture_node,udim_workflow)

        else:
            print("No file selected.")
    else:
        # If no material is selected, show warning
        cmds.warning("No valid aiStandardSurface material selected.")


if __name__ == "__main__":
    main()
