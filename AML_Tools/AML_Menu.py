"""
Arnold Maps Linker AML - v1.0.0
==========================
Automates the linking of texture maps in Maya based on JSON-based naming conventions.

Version: v1.0.0
Copyright (c) 2024 Mohab Younes
Licensed under the MIT License. See the LICENSE file for details.
"""

from maya.mel import eval
from maya.app.general import nodeEditorMenus
from maya import cmds as cmds
from PySide2 import QtWidgets, QtCore


def addpmamenuitems(ned , node):

    node_type = cmds.nodeType(node)

    if node_type == "aiStandardSurface":
        # Check if the menu item already exists to prevent duplication
        existing_menu = cmds.menuItem("LinkMaterial", exists=True)
        if not existing_menu:
            cmds.menuItem("LinkMaterial", label="(AML) Link Textures ", c=linkmaterial)

        return True
    else:
        return False


def run_texture_manager (*args):
    try:
        script_name = "Texture_name_manager"  # Replace with your actual script name (without the ".py")
        eval('python("from AML_Tools import {}; {}.show_texture_manager_ui()")'.format(script_name, script_name))
    except Exception as e:
        cmds.error("Failed to execute the script: {}".format(e))

def linkmaterial(*args):
    try:
        script_name = "Link_Material"  # Replace with your actual script name (without the ".py")
        eval('python("from AML_Tools import {}; {}.main()")'.format(script_name, script_name))
    except Exception as e:
        cmds.error("Failed to execute the script: {}".format(e))


def show_about_dialog(*args):
    # Create a QApplication if one doesn't already exist
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    # Create the dialog
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("About Developer")


    # Create a layout
    layout = QtWidgets.QVBoxLayout(dialog)

    # Developer name and description
    name_label = QtWidgets.QLabel("<b>Developer :</b> Mohab Younes")
    name_label.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(name_label)

    # Copyright info
    copyright_label = QtWidgets.QLabel(
        "<b> 2024 Mohab Younes. Licensed under the MIT License. All Rights Reserved.</b>")
    copyright_label.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(copyright_label)

    # Add LinkedIn hyperlink
    linkedin_label = QtWidgets.QLabel('<a href="https://www.linkedin.com/in/mohab-younes/" style="color:#FF6347;">LinkedIn</a>')
    linkedin_label.setOpenExternalLinks(True)  # Enable hyperlink behavior
    layout.addWidget(linkedin_label)

    # Add GitHub hyperlink
    github_label = QtWidgets.QLabel('<a href="https://github.com/M0HabYounes" style="color:#FF6347;">GitHub</a>')
    github_label.setOpenExternalLinks(True)  # Enable hyperlink behavior
    layout.addWidget(github_label)

    # Add email hyperlink (new addition)
    email_label = QtWidgets.QLabel('<a href="mailto:mohabyouneswork@gmail.com" style="color:#FF6347;">Email</a>')
    email_label.setOpenExternalLinks(True)  # Enable hyperlink behavior
    layout.addWidget(email_label)

    # Add a thank-you message for the user
    thank_you_label = QtWidgets.QLabel("<i>Thank you for using the tool!</i>")
    thank_you_label.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(thank_you_label)

    # Add a close button
    close_button = QtWidgets.QPushButton("Close")
    close_button.clicked.connect(dialog.close)
    layout.addWidget(close_button)

    # Styling the dialog window to make it more visually appealing
    dialog.setStyleSheet("""
        QDialog {
            background-color: #2b2b2b;
        }
        QLabel {
            font-size: 12px; /* Simplified font size */
            font-family: Arial, sans-serif;
            color: #f4f1f0;
        }
        QLabel a {
            color: #FF6347;  /* New hyperlink color: Tomato */
            text-decoration: none;
        }
        QLabel a:hover {
            color: #FFD700;  /* Color on hover: Gold */
        }
        QPushButton {
            background-color: #FF6347;  /* Changed button color to match hyperlink */
            color: white;
            border-radius: 5px;
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: #FF4500; /* Brighter red on hover */
        }
    """)

    # Show the dialog
    dialog.exec_()
def create_menu () :
# Check if the custom menu already exists, if so, delete it
    if cmds.menu('AML_Menu', exists=True):
        cmds.deleteUI('AML_Menu')

    # Create the custom menu under the main window
    menu_obj = 'AML_Menu'
    menu_label = 'AML Menu'
    custom_tools_menu = cmds.menu(menu_obj, label=menu_label, parent='MayaWindow')

    # Check if the menu item already exists, if so, skip adding it
    if not cmds.menuItem("TextureManager", exists=True):
        # Add the "Texture Manage" item
        cmds.menuItem("TextureManager", label="Texture Manager", parent=custom_tools_menu, command=run_texture_manager)

    if not cmds.menuItem("Link", exists=True):
        # Add the "Link" item
        cmds.menuItem("Link", label="Link Textures", parent=custom_tools_menu, command=linkmaterial)

    if not cmds.menuItem("About", exists=True):
        # Add the "About" item
        cmds.menuItem("About", label="About", parent=custom_tools_menu, command=show_about_dialog)
def run():
    create_menu()
    nodeEditorMenus.customInclusiveNodeItemMenuCallbacks.append(addpmamenuitems)
