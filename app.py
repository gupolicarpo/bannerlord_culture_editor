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
    # Parse the uploaded culture file
    tree = ET.parse(culture_file)
    root = tree.getroot()
    
    # Create a list of all relevant IDs from the culture file (troops, culture IDs, etc.)
    culture_dict = {}

    # Parse for the relevant IDs: troop IDs and culture IDs
    for elem in root.iter():
        if elem.tag in ['melee_militia_troop', 'basic_troop', 'elite_basic_troop', 'ranged_militia_troop', 'culture']:
            culture_dict[elem.attrib['id']] = elem.tag
    
    # Display a dropdown menu to select the ID to edit
    if culture_dict:
        troop_id_to_edit = st.selectbox('Select Troop or Culture ID to Edit', list(culture_dict.keys()))

        # Input field to allow user to change the ID
        new_id = st.text_input('New ID', value=troop_id_to_edit)

        # Step 3: Apply changes when the "Apply Changes" button is clicked
        if st.button("Apply Changes"):
            if new_id and troop_id_to_edit != new_id:
                st.write(f"Updating {troop_id_to_edit} to {new_id} across all relevant files...")

                # Update the relevant files with the new ID
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
            else:
                st.warning("Please enter a valid new ID.")
