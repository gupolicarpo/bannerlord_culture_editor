import streamlit as st
import xml.etree.ElementTree as ET
import os
import tempfile
import zipfile
import io

# Function to read and parse an XML file
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return tree, root

# Function to save the modified XML tree back to file
def save_xml(tree, file_path):
    tree.write(file_path)

# Function to propagate changes to related files based on spcultures_vlandia.xml
def propagate_changes_to_related_files(modified_data, uploaded_files):
    """
    Given the modified data (e.g., NPC names, equipment, traits in spcultures_vlandia.xml),
    propagate the changes to all related files.
    """
    updated_files = []  # List to store paths of updated files

    # Iterate through each file and apply the changes based on the modified data
    for file in uploaded_files:
        tree, root = parse_xml(file)
        
        # Modify the culture, NPC names, equipment, or other elements based on the modified data
        if 'spcultures_vlandia.xml' in file:
            # For the culture file itself, we will be changing NPC names, culture ID, etc.
            for elem in root.iter():
                # Example: Update culture name
                if elem.tag == 'culture' and elem.text == modified_data.get('old_culture'):
                    elem.text = modified_data.get('new_culture')
                
                # Example: Update NPC names
                if elem.tag == 'name' and elem.text == modified_data.get('old_npc_name'):
                    elem.text = modified_data.get('new_npc_name')

                # Example: Update equipment IDs
                if elem.tag == 'equipment' and elem.text == modified_data.get('old_equipment_id'):
                    elem.text = modified_data.get('new_equipment_id')

        # For other files, propagate the relevant changes (NPC names, equipment IDs)
        else:
            for elem in root.iter():
                # Example: Update NPC names in NPC character files
                if elem.tag == 'name' and elem.text == modified_data.get('old_npc_name'):
                    elem.text = modified_data.get('new_npc_name')

                # Example: Update equipment IDs
                if elem.tag == 'equipment' and elem.text == modified_data.get('old_equipment_id'):
                    elem.text = modified_data.get('new_equipment_id')

                # Handle other specific changes as needed, such as culture IDs, traits, etc.

        # Save the modified file
        save_xml(tree, file)
        updated_files.append(file)

    return updated_files

# Function to zip the updated files
def zip_files(file_paths):
    # Create a BytesIO buffer to hold the zip file
    zip_buffer = io.BytesIO()

    # Create a zip file in memory
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path, os.path.basename(file_path))

    # Move to the beginning of the buffer
    zip_buffer.seek(0)
    return zip_buffer

# Main Streamlit app
def main():
    st.title("Vlandia Culture Mod Editor")
    st.write("Upload the necessary files, modify NPCs, equipment, and other data in spcultures_vlandia.xml and propagate changes across all related files.")

    # Step 1: File Upload Section
    uploaded_files = st.file_uploader("Upload XML files", type=["xml"], accept_multiple_files=True)
    
    if uploaded_files:
        # Save uploaded files temporarily in a temporary directory
        uploaded_file_paths = []
        with tempfile.TemporaryDirectory() as tempdir:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(tempdir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                uploaded_file_paths.append(file_path)
            
            st.write("Files uploaded successfully. Now, make the modifications!")

            # Step 2: Modify Data (for example, NPC names, culture ID)
            modified_data = {
                "old_culture": "Culture.wulf",  # Old culture ID
                "new_culture": "Culture.new_culture",  # New culture ID
                "old_npc_name": "Old NPC Name",  # NPC name to change
                "new_npc_name": "New NPC Name",  # New NPC name
                "old_equipment_id": "Item.old_equipment",  # Old equipment ID
                "new_equipment_id": "Item.new_equipment"  # New equipment ID
            }

            # Allow the user to trigger the changes
            if st.button('Propagate Changes'):
                updated_files = propagate_changes_to_related_files(modified_data, uploaded_file_paths)
                st.success("Changes have been successfully propagated across all files!")

                # Step 3: Zip and Download
                # Create a zipped file with the updated files
                zip_buffer = zip_files(updated_files)

                # Provide the download button
                st.download_button(
                    label="Download Updated Files",
                    data=zip_buffer,
                    file_name="modified_vlandia_files.zip",
                    mime="application/zip"
                )

if __name__ == '__main__':
    main()







