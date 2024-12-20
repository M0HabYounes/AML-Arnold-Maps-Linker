"""
Arnold Maps Linker AML - v1.0.0
==========================
Automates the linking of texture maps in Maya based on JSON-based naming conventions.

Version: v1.0.0
Copyright (c) 2024 Mohab Younes
Licensed under the MIT License. See the LICENSE file for details.
"""

import maya.cmds as cmds
import json

# Save the JSON path using Maya's optionVar
def save_json_path(json_path):
    cmds.optionVar(sv=("json_file_path", json_path))
# Retrieve the saved JSON path
def get_saved_json_path():
    return cmds.optionVar(q="json_file_path") if cmds.optionVar(exists="json_file_path") else None

def load_texture_data_from_json():
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

# Save texture data to the JSON file
def save_texture_data_to_json(texture_data):
    json_file = get_saved_json_path()
    with open(json_file, 'w') as file:
        json.dump(texture_data, file, indent=4)

def toggle_prefer_exr(checked):
    texture_data = load_texture_data_from_json()

    # Add or update the "prefer_exr" entry globally
    texture_data["prefer_exr"] = bool(checked)

    # Save the updated JSON
    save_texture_data_to_json(texture_data)

def toggle_udim(checked):
    texture_data = load_texture_data_from_json()

    # Add or update the "prefer_exr" entry globally
    texture_data["udim"] = bool(checked)

    # Save the updated JSON
    save_texture_data_to_json(texture_data)


# Add alternative texture names to the corresponding list and JSON file
def add_texture_name(*args):
    # Get the entered alternative names from the text field
    alternative_names = cmds.textField(alternative_names_input, query=True, text=True).strip()

    if alternative_names:
        # Split the alternative names by commas and strip any extra spaces
        alternative_names_list = [name.strip() for name in alternative_names.split(",")]

        # Get the selected tab
        selected_tab = cmds.tabLayout(tab_layout, query=True, selectTab=True)

        # Create a string for displaying the names in the list
        texture_display_str = ", ".join(alternative_names_list)

        # Map the selected tab to the corresponding texture type
        if selected_tab == "BaseColor":
            texture_type = "BaseColor"
        elif selected_tab == "Roughness":
            texture_type = "Roughness"
        elif selected_tab == "Metallic":
            texture_type = "Metallic"
        elif selected_tab == "Normal":
            texture_type = "Normal"
        elif selected_tab == "Height":
            texture_type = "Height"
        elif selected_tab == "Specular":
            texture_type = "Specular"
        elif selected_tab == "Opacity":
            texture_type = "Opacity"
        else:
            texture_type = None  # Default value if no valid tab is selected

        # Ensure texture_type is valid before proceeding
        if texture_type:
            # Load the current texture data from the JSON file
            texture_data = load_texture_data_from_json()

            # Check for duplicates in the existing texture list for the selected texture type
            existing_names = [texture['name'] for texture in texture_data.get(texture_type, [])]

            # Check for any duplicates in the alternative_names_list
            duplicates = [name for name in alternative_names_list if name in existing_names]

            if duplicates:
                # Show a warning if duplicates are found and stop the addition process
                cmds.confirmDialog(title="Duplicate Texture Name",
                                   message="The following texture names already exist: \n" + "\n".join(duplicates),
                                   button=["OK"], defaultButton="OK")
            else:
                # If no duplicates, add the names to the list with "locked": false
                texture_objects = [{"locked": False, "name": name} for name in alternative_names_list]

                # Add the new texture objects to the corresponding texture type list
                if texture_type in texture_data:
                    texture_data[texture_type].extend(texture_objects)
                else:
                    texture_data[texture_type] = texture_objects

                # Save the updated texture data back to the JSON file
                save_texture_data_to_json(texture_data)

                # Add the names to the UI list
                if selected_tab == "BaseColor":
                    cmds.textScrollList(base_color_list, edit=True, append=texture_display_str)
                elif selected_tab == "Roughness":
                    cmds.textScrollList(roughness_list, edit=True, append=texture_display_str)
                elif selected_tab == "Metallic":
                    cmds.textScrollList(metallic_list, edit=True, append=texture_display_str)
                elif selected_tab == "Normal":
                    cmds.textScrollList(normal_list, edit=True, append=texture_display_str)
                elif selected_tab == "Height":
                    cmds.textScrollList(height_list, edit=True, append=texture_display_str)
                elif selected_tab == "Opacity":
                    cmds.textScrollList(opacity_list, edit=True, append=texture_display_str)

        # Clear the input field after adding the names
        cmds.textField(alternative_names_input, edit=True, text="")

# Delete selected texture name from the list and update the JSON file
def delete_texture_name(*args):
    selected_tab = cmds.tabLayout(tab_layout, query=True, selectTab=True)

    # Get the selected texture name from the list
    if selected_tab == "BaseColor":
        selected_name = cmds.textScrollList(base_color_list, query=True, selectItem=True)
        texture_type = "BaseColor"
    elif selected_tab == "Roughness":
        selected_name = cmds.textScrollList(roughness_list, query=True, selectItem=True)
        texture_type = "Roughness"
    elif selected_tab == "Metallic":
        selected_name = cmds.textScrollList(metallic_list, query=True, selectItem=True)
        texture_type = "Metallic"
    elif selected_tab == "Normal":
        selected_name = cmds.textScrollList(normal_list, query=True, selectItem=True)
        texture_type = "Normal"
    elif selected_tab == "Height":
        selected_name = cmds.textScrollList(height_list, query=True, selectItem=True)
        texture_type = "Height"
    elif selected_tab == "Opacity":
        selected_name = cmds.textScrollList(opacity_list, query=True, selectItem=True)
        texture_type = "Opacity"
    else:
        selected_name = None
        texture_type = None

    # If a texture name is selected, remove it
    if selected_name and texture_type:
        selected_name = selected_name[0]  # Get the first selected item

        # Load the current texture data from the JSON file
        texture_data = load_texture_data_from_json()

        # Find the texture object in the texture type list
        texture_to_remove = None
        for texture in texture_data.get(texture_type, []):
            if texture["name"] == selected_name:
                texture_to_remove = texture
                break

        # If the texture is found and not locked, remove it
        if texture_to_remove:
            if texture_to_remove["locked"]:
                cmds.confirmDialog(title="Locked Texture Name",
                                   message="This texture name is locked and cannot be deleted.",
                                   button=["OK"], defaultButton="OK")
            else:
                # Remove the texture from the list in JSON
                texture_data[texture_type].remove(texture_to_remove)

                # Save the updated texture data back to the JSON file
                save_texture_data_to_json(texture_data)

                # Remove the selected name from the list UI
                if selected_tab == "BaseColor":
                    cmds.textScrollList(base_color_list, edit=True, removeItem=selected_name)
                elif selected_tab == "Roughness":
                    cmds.textScrollList(roughness_list, edit=True, removeItem=selected_name)
                elif selected_tab == "Metallic":
                    cmds.textScrollList(metallic_list, edit=True, removeItem=selected_name)
                elif selected_tab == "Normal":
                    cmds.textScrollList(normal_list, edit=True, removeItem=selected_name)
                elif selected_tab == "Height":
                    cmds.textScrollList(height_list, edit=True, removeItem=selected_name)
                elif selected_tab == "Opacity":
                    cmds.textScrollList(opacity_list, edit=True, removeItem=selected_name)
# Function to update the displayed list for the selected texture type tab

def update_texture_list(*args):
    selected_tab = cmds.tabLayout(tab_layout, query=True, selectTab=True)
    texture_data = load_texture_data_from_json()

    # Clear all lists first to avoid duplicates
    cmds.textScrollList(base_color_list, edit=True, removeAll=True)
    cmds.textScrollList(roughness_list, edit=True, removeAll=True)
    cmds.textScrollList(metallic_list, edit=True, removeAll=True)
    cmds.textScrollList(normal_list, edit=True, removeAll=True)
    cmds.textScrollList(height_list, edit=True, removeAll=True)
    cmds.textScrollList(opacity_list, edit=True, removeAll=True)

    # Display the appropriate list for the selected tab
    if selected_tab == "BaseColor" and ("Base"
                                        "Color") in texture_data:
        for texture in texture_data["BaseColor"]:
            texture_name = texture["name"]
            cmds.textScrollList(base_color_list, edit=True, append=texture_name)
    elif selected_tab == "Roughness" and "Roughness" in texture_data:
        for texture in texture_data["Roughness"]:
            texture_name = texture["name"]
            cmds.textScrollList(roughness_list, edit=True, append=texture_name)
    elif selected_tab == "Metallic" and "Metallic" in texture_data:
        for texture in texture_data["Metallic"]:
            texture_name = texture["name"]
            cmds.textScrollList(metallic_list, edit=True, append=texture_name)
    elif selected_tab == "Normal" and "Normal" in texture_data:
        for texture in texture_data["Normal"]:
            texture_name = texture["name"]
            cmds.textScrollList(normal_list, edit=True, append=texture_name)
    elif selected_tab == "Height" and "Height" in texture_data:
        for texture in texture_data["Height"]:
            texture_name = texture["name"]
            cmds.textScrollList(height_list, edit=True, append=texture_name)
    elif selected_tab == "Opacity" and "Opacity" in texture_data:
        for texture in texture_data["Opacity"]:
            texture_name = texture["name"]
            cmds.textScrollList(opacity_list, edit=True, append=texture_name)

    # Update the placeholder for the input field based on the selected tab
    if selected_tab == "BaseColor":
        cmds.textField(alternative_names_input, edit=True,
                       placeholderText="Enter Base Color texture names (e.g., Diffuse, Albedo)")
    elif selected_tab == "Roughness":
        cmds.textField(alternative_names_input, edit=True,
                       placeholderText="Enter Roughness texture names (e.g., Roughness)")
    elif selected_tab == "Metallic":
        cmds.textField(alternative_names_input, edit=True,
                       placeholderText="Enter Metallic texture names (e.g., Metalness)")
    elif selected_tab == "Normal":
        cmds.textField(alternative_names_input, edit=True,
                       placeholderText="Enter Normal texture names (e.g., Normal Map)")
    elif selected_tab == "Height":
        cmds.textField(alternative_names_input, edit=True,
                       placeholderText="Enter Height texture names (e.g., Displacement)")
    elif selected_tab == "Specular":
        cmds.textField(alternative_names_input, edit=True,
                       placeholderText="Enter Specular texture names (e.g., Specular)")
    elif selected_tab == "Opacity":
        cmds.textField(alternative_names_input, edit=True,
                       placeholderText="Enter Opacity texture names (e.g., Opacity)")

    prefer_exr_value = texture_data.get("prefer_exr", False)  # Default to False if not present
    cmds.checkBox(prefer_exr_checkbox, edit=True, value=prefer_exr_value)

    udim_value = texture_data.get("udim", False)  # Default to False if not present
    cmds.checkBox(udim_workflow_checkbox, edit=True, value=udim_value)
# Create the UI
def show_texture_manager_ui():
    # Check if the window exists and delete it if it does
    if cmds.window("textureManagerWindow", exists=True):
        cmds.deleteUI("textureManagerWindow", window=True)

    # Create a new window
    cmds.window("textureManagerWindow", title="AML: TextureName Manager", widthHeight=(410, 350))

    # Create a column layout for the UI elements
    cmds.columnLayout(adjustableColumn=True)

    # Input fields and buttons that will be present across all tabs
    global alternative_names_input
    alternative_names_input = cmds.textField("alternativeNamesInput",
                                             placeholderText="Enter alternative names (comma separated)",
                                             width=300,
                                             height=35)

    # Add texture name button
    cmds.button(label="Add Texture Name", command=add_texture_name, width=200)

    # Delete texture name button
    cmds.button(label="Delete Texture Name", command=delete_texture_name, width=200)
    # Refresh button
    cmds.button(label="Refresh", command=update_texture_list, width=200)

    cmds.separator(height= 7, style='none')

    global udim_workflow_checkbox
    udim_workflow_checkbox = cmds.checkBox(label="UDIM's Workflow" , align = 'center' , changeCommand= toggle_udim)
    cmds.separator(height= 7, style='none')

    # Create the tab layout for different texture types

    global tab_layout
    tab_layout = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    # Define the tabs for the texture types
    cmds.columnLayout("BaseColor", parent=tab_layout)
    cmds.text(label="Enter names for Base Color (e.g., Diffuse, Albedo)")
    cmds.separator(height= 4, style='none')

    global base_color_list
    base_color_list = cmds.textScrollList(allowMultiSelection=False, width=200, height=150)

    cmds.columnLayout("Roughness", parent=tab_layout)
    cmds.text(label="Enter names for Roughness (e.g., Roughness)")
    cmds.separator(height= 4, style='none')

    global roughness_list
    roughness_list = cmds.textScrollList(allowMultiSelection=False, width=200, height=150)

    cmds.columnLayout("Metallic", parent=tab_layout)
    cmds.text(label="Enter names for Metallic (e.g., Metalness)")
    cmds.separator(height= 4, style='none')

    global metallic_list
    metallic_list = cmds.textScrollList(allowMultiSelection=False, width=200, height=150)

    cmds.columnLayout("Normal", parent=tab_layout)
    cmds.text(label="Enter names for Normal (e.g., Normal)")
    cmds.separator(height= 4, style='none')


    global normal_list
    normal_list = cmds.textScrollList(allowMultiSelection=False, width=200, height=150)

    cmds.columnLayout("Height", parent=tab_layout)
    cmds.text(label="Enter names for Height (e.g., Displacement)")
    cmds.separator(height= 4, style='none')

    global height_list
    height_list = cmds.textScrollList(allowMultiSelection=False, width=200, height=150)

    global prefer_exr_checkbox
    prefer_exr_checkbox = cmds.checkBox(label="Prefer *.exr", changeCommand=toggle_prefer_exr)


    cmds.columnLayout("Opacity", parent=tab_layout)
    cmds.text(label="Enter names for Opacity (e.g., Opacity)")
    cmds.separator(height= 4, style='none')

    global opacity_list
    opacity_list = cmds.textScrollList(allowMultiSelection=False, width=200, height=150)

    # Load texture data from the JSON file and display them
    update_texture_list()

    # Update the displayed list based on selected tab
    cmds.tabLayout(tab_layout, edit=True, changeCommand=update_texture_list)



    # Show the window
    cmds.showWindow("textureManagerWindow")
# Show the Texture Manager UI
show_texture_manager_ui()
