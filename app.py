import streamlit as st
import xml.etree.ElementTree as ET
from io import StringIO

# Step 1: Upload Files
st.title("Khuzait Culture Modding App")

# File upload for culture file and related mod files
culture_file = st.file_uploader('Upload sp_cultures_khuzait.xml', type='xml')
other_files = {
    "spnpccharacters_khuzait.xml": st.file_uploader('Upload spnpccharacters_khuzait.xml', type='xml'),
    "partyTemplates_khuzait.xml": st.file_uploader('Upload partyTemplates_khuzait.xml', type='xml'),
    "spnpccharactertemplates_khuzait.xml": st.file_uploader('Upload spnpccharactertemplates_khuzait.xml', type='xml'),
    "spclans_khuzait.xml": st.file_uploader('Upload spclans_khuzait.xml', type='xml'),
    "spgenericcharacters_khuzait.xml": st.file_uploader('Upload spgenericcharacters_khuzait.xml', type='xml'),
    "sandbox_equipment_sets_khuzait.xml": st.file_uploader('Upload sandbox_equipment_sets_khuzait.xml', type='xml'),
    "sandboxcore_equipment_sets_khuzait.xml": st.file_uploader('Upload sandboxcore_equipment_sets_khuzait.xml', type='xml'),
    "spheroes_khuzait.xml": st.file_uploader('Upload spheroes_khuzait.xml', type='xml'),
    "spkingdoms_khuzait.xml": st.file_uploader('Upload spkingdoms_khuzait.xml', type='xml'),
    "spspecialcharacters_khuzait.xml": st.file_uploader('Upload spspecialcharacters_khuzait.xml', type='xml'),
    "sandbox_character_templates_khuzait.xml": st.file_uploader('Upload sandbox_character_templates_khuzait.xml', type='xml'),
    "sp_hero_templates_khuzait.xml": st.file_uploader('Upload sp_hero_templates_khuzait.xml', type='xml')
}

# Step 2: Parse the culture file and detect changes
if culture_file:
    tree = ET.parse(culture_file)
    root = tree.getroot()
    
    # Identify IDs that can be modified
    culture_dict = {}
    for elem in root.iter():
        if elem.tag == 'melee_militia_troop':  # Look for troop IDs
            culture_dict[elem.attrib['id']] = 'melee_militia_troop'
        if elem.tag == 'basic_troop':  # Look for basic troops
            culture_dict[elem.attrib['id']] = 'basic_troop'
        if elem.tag == 'elite_basic_troop':  # Look for elite basic troops
            culture_dict[elem.attrib['id']] = 'elite_basic_troop'
        if elem.tag == 'ranged_militia_troop':  # Look for ranged troops
            culture_dict[elem.attrib['id']] = 'ranged_militia_troop'
        if elem.tag == 'culture':  # Look for culture ID
            culture_dict[elem.attrib['id']] = 'culture'

    # Show the available troop IDs to edit
    troop_id_to_edit = st.selectbox('Select Troop or Culture ID to Edit', list(culture_dict.keys()))

    # Input new ID for the selected troop
    new_id = st.text_input('New ID', value=troop_id_to_edit)

    # Step 3: Update related files when a change is detected
    if new_id and troop_id_to_edit != new_id:
        st.write(f"Updating {troop_id_to_edit} to {new_id} across all relevant files...")

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
                            elem.set(key, new_id)
                
                # Save the updated file in memory
                updated_files[filename] = tree

        # Step 4: Provide download options for updated files
        for filename, updated_tree in updated_files.items():
            output = StringIO()
            updated_tree.write(output, encoding='utf-8', xml_declaration=True)
            st.download_button(label=f"Download updated {filename}", data=output.getvalue(), file_name=filename)


