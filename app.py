import streamlit as st
import xml.etree.ElementTree as ET
import tempfile
import zipfile
import io
import os

# Function to read and parse an XML file
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return tree, root

# Function to extract all relevant data from spcultures_vlandia.xml
def extract_culture_data(file_path):
    tree, root = parse_xml(file_path)
    culture_data = {}

    # Extract relevant data like culture ID, NPC names, equipment, etc.
    for elem in root.iter():
        if elem.tag == 'culture':  # Assuming culture ID is in <culture> tags
            culture_data['culture_id'] = elem.text
        elif elem.tag == 'name':  # Assuming NPC names are stored under <name> tags
            if 'npc_names' not in culture_data:
                culture_data['npc_names'] = []
            culture_data['npc_names'].append(elem.text)
        elif elem.tag == 'equipment':  # Assuming equipment IDs are stored under <equipment> tags
            if 'equipment_ids' not in culture_data:
                culture_data['equipment_ids'] = []
            culture_data['equipment_ids'].append(elem.text)
        # Add more tags to extract data for other relevant fields like traits, skills, etc.

    return culture_data

# Function to save the modified XML tree back to file
def save_xml(tree, file_path):
    tree.write(file_path)

# Function to propagate changes to related files
def propagate_changes_to_related_files(modified_data, uploaded_files):
    """
    Given the modified data, propagate the changes to all related files.
    """
    updated_files = []  # List to store paths of updated files

    # Iterate through each file and apply the changes based on the modified data
    for file in uploaded_files:
        tree, root = parse_xml(file)
        
        # Apply changes to spcultures_vlandia.xml (or any other file)
        for elem in root.iter():
            if elem.tag == 'culture' and elem.text == modified_data.get('old_culture'):
                elem.text = modified_data.get('new_culture')
            
            if elem.tag == 'name' and elem.text == modified_data.get('old_npc_name'):
                elem.text = modified_data.get('new_npc_name')
            
            if elem.tag == 'equipment' and elem.text == modified_data.get('old_equipment_id'):
                elem.text = modified_data.get('new_equipment_id')

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

            # Step 2: Extract Data from spcultures_vlandia.xml
            culture_data = {}
            for file_path in uploaded_file_paths:
                if 'spcultures_vlandia.xml' in file_path:
                    culture_data = extract_culture_data(file_path)
                    break

            if culture_data:
                # Pre-populate the form with extracted data
                with st.form("modify_data"):
                    # Editable fields pre-filled with the extracted data
                    old_culture = st.text_input("Old Culture ID", value=culture_data.get('culture_id', ''))
                    new_culture = st.text_input("New Culture ID", value=f"{culture_data.get('culture_id', '')}_modified")

                    old_npc_name = st.text_input("Old NPC Name", value=culture_data.get('npc_names', [])[0] if culture_data.get('npc_names') else '')
                    new_npc_name = st.text_input("New NPC Name", value=f"{culture_data.get('npc_names', [])[0]}_modified" if culture_data.get('npc_names') else '')

                    old_equipment_id = st.text_input("Old Equipment ID", value=culture_data.get('equipment_ids', [])[0] if culture_data.get('equipment_ids') else '')
                    new_equipment_id = st.text_input("New Equipment ID", value=f"{culture_data.get('equipment_ids', [])[0]}_modified" if culture_data.get('equipment_ids') else '')

                    # Submit button
                    submit_button = st.form_submit_button(label="Apply Changes")

                    if submit_button:
                        # Create modified data
                        modified_data = {
                            "old_culture": old_culture,
                            "new_culture": new_culture,
                            "old_npc_name": old_npc_name,
                            "new_npc_name": new_npc_name,
                            "old_equipment_id": old_equipment_id,
                            "new_equipment_id": new_equipment_id
                        }

                        # Step 3: Propagate Changes and Generate Downloadable Zip
                        updated_files = propagate_changes_to_related_files(modified_data, uploaded_file_paths)
                        st.success("Changes have been successfully propagated across all files!")

                        # Step 4: Zip and Download
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
