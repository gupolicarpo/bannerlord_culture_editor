import xml.etree.ElementTree as ET

def load_xml(file_path):
    """Load and parse an XML file."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root, tree
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
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
    
    # You can extend this for other types of troops (e.g., ranged, militia) as needed.
    return troop_ids

def update_npc_character(npc_root, npc_id, new_npc_id):
    """Update the NPC ID in the npc character XML file."""
    for npc in npc_root.findall(".//NPCCharacter"):
        if npc.attrib.get("id") == npc_id:
            print(f"Updating NPC Character: {npc_id} -> {new_npc_id}")
            npc.set("id", new_npc_id)  # Change the NPC ID
            # You can add further modifications here, like updating skills or equipment if needed.
            return True
    return False

def main():
    # Load the central culture file
    spcultures_root, _ = load_xml('spcultures_khuzait.xml')
    
    if spcultures_root is None:
        return
    
    # Extract troop IDs from the culture file
    troop_ids = extract_troop_ids(spcultures_root)
    print(f"Troop IDs to update: {troop_ids}")
    
    # Load the related files
    spnpccharacters_root, spnpccharacters_tree = load_xml('spnpccharacters_khuzait.xml')
    
    # For each troop ID in spcultures, update in the NPC character file
    for troop_id in troop_ids:
        new_troop_id = 'wulf_nomad'  # Example of changing the NPC ID
        updated = update_npc_character(spnpccharacters_root, troop_id, new_troop_id)
        if updated:
            spnpccharacters_tree.write('spnpccharacters_khuzait.xml')  # Save the updated file
            print(f"Updated {troop_id} to {new_troop_id}")

if __name__ == "__main__":
    main()
