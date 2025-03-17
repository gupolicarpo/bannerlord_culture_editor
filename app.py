import streamlit as st
import xml.etree.ElementTree as ET
from io import StringIO

# Step 1: File upload
st.title('Khuzait Culture Modding App')

# Upload the culture file and related mod files
culture_file = st.file_uploader('Upload sp_cultures_khuzait.xml', type='xml')
other_files = {
    "spnpccharacters_khuzait.xml": st.file_uploader('Upload spnpccharacters_khuzait.xml', type='xml'),
    "partyTemplates_khuzait.xml": st.file_uploader('Upload partyTemplates_khuzait.xml', type='xml'),
    "spnpccharactertemplates_khuzait.xml": st.file_uploader('Upload spnpccharactertemplates_khuzait.xml', type='xml'),
    "spclans_khuzait.xml": st.file_uploader('Upload spclans_khuzait.xml', type='xml'),
}

# Step 2: Parse the culture file and detect changes
if culture_file:
    tree = ET.parse(culture_file)
    root = tree.getroot()
    
    # Identify IDs that we may modify
    culture_dict = {}
    for elem in root.iter():
        if elem.tag == 'melee_militia_troop':  # Look for troop IDs
            culture_dict[elem.attrib['id']] = 'melee_militia_troop'

    # Show the available troop IDs to edit
    troop_id_to_edit = st.selectbox('Select Troop ID to Edit', list(culture_dict.keys()))

    # Input new ID for the selected troop
    new_troop_id = st.text_input('New Troop ID', value=troop_id_to_edit)

    # Step 3: Update related files when a change is detected
    if new_troop_id and troop_id_to_edit != new_troop_id:
        st.write(f"Updating {troop_id_to_edit} to {new_troop_id} across other files...")

        # Update each related file
        updated_files = {}

        for filename, file in other_files.items():
            if file:
                # Read the file content
                file_content = file.getvalue().decode("utf-8")
                tree = ET.ElementTree(ET.fromstring(file_content))
                root = tree.getroot()

                # Search and update all references to the old ID
                for elem in root.iter():
                    for key, value in elem.attrib.items():
                        if value == troop_id_to_edit:
                            elem.set(key, new_troop_id)
                
                # Save the updated file in memory
                updated_files[filename] = tree

        # Step 4: Provide download options for updated files
        for filename, updated_tree in updated_files.items():
            output = StringIO()
            updated_tree.write(output, encoding='utf-8', xml_declaration=True)
            st.download_button(label=f"Download updated {filename}", data=output.getvalue(), file_name=filename)


