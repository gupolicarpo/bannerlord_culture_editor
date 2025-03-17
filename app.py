import xml.etree.ElementTree as ET
import streamlit as st

def load_xml(file_path):
    """Load and parse an XML file."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root, tree
    except Exception as e:
        st.error(f"Error loading file {file_path}: {e}")
        return None, None

def extract_troop_ids(spcultures_root):
    """Extract troop IDs from the spcultures_khuzait.xml file."""
    troop_ids = []
    
    # Extract basic and elite basic troops
    basic_troop = spcultures_root.find(".//basic_troop")
    elite_basic_troop = spcultures_root.find(".//elite_basic_troop")
    
    if basic_troop is not None:
        troop_ids.append(basic_troop.text.strip())
    
    if elite_basic_troop is not None:
        troop_ids.append(elite_basic_troop.text.strip())
    
    return troop_ids

def update_npc_character(npc_root, npc_id, new_npc_id):
    """Update the NPC ID in the npc character XML file."""
    updated = False
    for npc in npc_root.findall(".//NPCCharacter"):
        if npc.attrib.get("id") == npc_id:
            npc.set("id", new_npc_id)  # Change the NPC ID
            updated = True
    return updated

def main():
    st.title("Khuzait NPC ID Updater")

    # File upload feature for the user to select their XML files
    spcultures_file = st.file_uploader("Upload spcultures_khuzait.xml", type="xml")
    spnpccharacters_file = st.file_uploader("Upload spnpccharacters_khuzait.xml", type="xml")

    if spcultures_file and spnpccharacters_file:
        # Load and parse both XML files
        spcultures_root, _ = load_xml(spcultures_file)
        spnpccharacters_root, spnpccharacters_tree = load_xml(spnpccharacters_file)

        if spcultures_root and spnpccharacters_root:
            # Extract troop IDs from the central file
            troop_ids = extract_troop_ids(spcultures_root)
            st.write(f"Troop IDs to update: {troop_ids}")

            # Update NPC IDs in the NPC character file
            for troop_id in troop_ids:
                new_troop_id = 'wulf_nomad'  # Example of changing the NPC ID
                updated = update_npc_character(spnpccharacters_root, troop_id, new_troop_id)
                if updated:
                    spnpccharacters_tree.write("spnpccharacters_khuzait_updated.xml")  # Save the updated file
                    st.success(f"Updated {troop_id} to {new_troop_id}")

if __name__ == "__main__":
    main()

