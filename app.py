import streamlit as st
import xml.etree.ElementTree as ET
import os

# Function to read and parse an XML file
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return tree, root

# Function to save the modified XML tree back to file
def save_xml(tree, file_path):
    tree.write(file_path)

# Function to propagate changes to related files based on spcultures_vlandia.xml
def propagate_changes_to_related_files(modified_data):
    """
    Given the modified data (e.g., NPC names, equipment, traits in spcultures_vlandia.xml),
    propagate the changes to all related files.
    """
    xml_files = [
        '/mnt/data/spclans_vlandia.xml',
        '/mnt/data/education_character_templates_vlandia.xml',
        '/mnt/data/education_equipment_templates_vlandia.xml',
        '/mnt/data/heroes_vlandia.xml',
        '/mnt/data/lords_vlandia.xml',
        '/mnt/data/module_strings_vlandia_complete.xml',
        '/mnt/data/partyTemplates_vlandia.xml',
        '/mnt/data/sandboxcore_equipment_sets_vlandia.xml',
        '/mnt/data/troops_vlandia.xml',
        '/mnt/data/spgenericcharacters_vlandia.xml',
        '/mnt/data/spkingdoms_vlandia.xml',
        '/mnt/data/spnpccharacters_vlandia.xml',
        '/mnt/data/spspecialcharacters_vlandia.xml'
    ]

    # Iterate through each file and apply the changes based on the modified data
    for file in xml_files:
        tree, root = parse_xml(file)
        
        # Modify the culture, NPC names, equipment, or other elements based on the modified data
        if file == '/mnt/data/spcultures_vlandia.xml':
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

# Main Streamlit app
def main():
    st.title("Vlandia Culture Mod Editor")
    st.write("Update NPCs, equipment, and other data in the spcultures_vlandia.xml and propagate changes across all related files.")

    # Example: Modify NPC names, culture IDs, and equipment
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
        propagate_changes_to_related_files(modified_data)
        st.success("Changes have been successfully propagated across all files!")

if __name__ == '__main__':
    main()






