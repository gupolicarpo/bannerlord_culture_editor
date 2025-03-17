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
