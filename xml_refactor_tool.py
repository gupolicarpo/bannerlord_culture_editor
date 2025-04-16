# --- Imports ---
import streamlit as st
# import xml.etree.ElementTree as ET # No longer using standard ET directly
from lxml import etree # Import lxml's etree module
from io import BytesIO
import zipfile
import re

# --- Configuration ---
# Common attributes that reference IDs (add more as needed)
REFERENCE_ATTRIBUTES = {
    # Attribute Name : Prefix (or None if just ID, or special marker)
    "culture": "Culture.",
    "faction": "Faction.",
    "owner": "Hero.", # Can be Faction too, heuristic needed maybe - CURRENTLY ASSUMING HERO
    "default_group": None, # Often refers to troop groups, might need prefix?
    "occupation": None, # Sometimes links to Occupations enum, not necessarily an ID reference
    "skill_template": "SkillSet.",
    "is_template": None, # Boolean, ignore
    "default_party_template": "PartyTemplate.",
    "villager_party_template": "PartyTemplate.",
    "caravan_party_template": "PartyTemplate.",
    "elite_caravan_party_template": "PartyTemplate.",
    "militia_party_template": "PartyTemplate.",
    "rebels_party_template": "PartyTemplate.",
    "vassal_reward_party_template": "PartyTemplate.",
    "basic_troop": "NPCCharacter.",
    "elite_basic_troop": "NPCCharacter.",
    "melee_militia_troop": "NPCCharacter.",
    "ranged_militia_troop": "NPCCharacter.",
    "melee_elite_militia_troop": "NPCCharacter.",
    "ranged_elite_militia_troop": "NPCCharacter.",
    "tournament_master": "NPCCharacter.",
    "villager": "NPCCharacter.",
    "caravan_master": "NPCCharacter.",
    "armed_trader": "NPCCharacter.",
    "caravan_guard": "NPCCharacter.",
    "veteran_caravan_guard": "NPCCharacter.",
    "prison_guard": "NPCCharacter.",
    "guard": "NPCCharacter.",
    "blacksmith": "NPCCharacter.",
    "weaponsmith": "NPCCharacter.",
    "townswoman": "NPCCharacter.",
    "townswoman_infant": "NPCCharacter.", # Added based on user XML
    "townswoman_child": "NPCCharacter.",  # Added based on user XML
    "townswoman_teenager": "NPCCharacter.",# Added based on user XML
    "townsman": "NPCCharacter.",
    "townsman_infant": "NPCCharacter.",   # Added based on user XML
    "townsman_child": "NPCCharacter.",    # Added based on user XML
    "townsman_teenager": "NPCCharacter.", # Added based on user XML
    "village_woman": "NPCCharacter.",
    "villager_male_child": "NPCCharacter.",# Added based on user XML (renamed from villager_child)
    "villager_male_teenager": "NPCCharacter.",# Added based on user XML (renamed from villager_teenager)
    "villager_female_child": "NPCCharacter.",# Added based on user XML (renamed from village_woman_child)
    "villager_female_teenager": "NPCCharacter.",# Added based on user XML (renamed from village_woman_teenager)
    "ransom_broker": "NPCCharacter.",
    "gangleader_bodyguard": "NPCCharacter.",
    "merchant_notary": "NPCCharacter.",
    "artisan_notary": "NPCCharacter.",
    "preacher_notary": "NPCCharacter.",
    "rural_notable_notary": "NPCCharacter.",
    "shop_worker": "NPCCharacter.",
    "tavernkeeper": "NPCCharacter.",
    "taverngamehost": "NPCCharacter.",
    "musician": "NPCCharacter.",
    "tavern_wench": "NPCCharacter.",
    "armorer": "NPCCharacter.",
    "horseMerchant": "NPCCharacter.",
    "barber": "NPCCharacter.",
    "merchant": "NPCCharacter.",
    "beggar": "NPCCharacter.",
    "female_beggar": "NPCCharacter.",
    "female_dancer": "NPCCharacter.",
    "gear_practice_dummy": "NPCCharacter.", # Added based on user XML
    "weapon_practice_stage_1": "NPCCharacter.", # Added based on user XML
    "weapon_practice_stage_2": "NPCCharacter.", # Added based on user XML
    "weapon_practice_stage_3": "NPCCharacter.", # Added based on user XML
    "gear_dummy": "NPCCharacter.", # Added based on user XML
    "upgrade_target": "NPCCharacter.", # In troops.xml
    "id": "EQUIPMENT_ITEM_ID", # Special case: 'id' on Equipment/equipment tags often reference Items
    "slot": None, # Usually Item or Mount type, complex, ignore for now
    "skill": "Skill.",
    "lord_template": "NPCCharacter.", # In spcultures.xml lord_templates
    "rebellion_hero_template": "NPCCharacter.", # In spcultures.xml rebellion_hero_templates
    "tournament_team_template": "NPCCharacter.", # Patterns might be needed for specific tournament template IDs
    "basic_mercenary_troop": "NPCCharacter.", # In spcultures.xml basic_mercenary_troops
    "equipment_set": "EquipmentRoster.", # spnpccharacters, lords
    "civilian_equipment_set": "EquipmentRoster.",
    "battle_equipment_set": "EquipmentRoster.",
    "civilian": "EquipmentRoster.", # Can also be EquipmentRoster ID apparently
    "default_battle_equipment_roster": "EquipmentRoster.",
    "default_civilian_equipment_roster": "EquipmentRoster.",
    "duel_preset_equipment_roster": "EquipmentRoster.",
    "banner_bearer_troop": "NPCCharacter.",
    "formation": None, # Usually enum, ignore
    "mount": "Item.", # Often references mount item ID
    "harness": "Item.", # Often references harness item ID
    "name": "TEMPLATE_REFERENCE", # Attributes like template="NPCCharacter.xyz" inside notable_and_wanderer_templates etc.
    # Add more known reference attributes here based on testing
}

# --- Helper Functions ---

# Use lxml for parsing
def parse_xml(uploaded_file):
    """Parses an uploaded XML file using lxml."""
    try:
        uploaded_file.seek(0)
        content = uploaded_file.read() # Read as bytes
        # Clean potential BOM
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]
        # Configure lxml parser to try and preserve comments and structure
        # remove_blank_text=True helps with pretty print output later
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
        root = etree.fromstring(content, parser=parser)
        tree = etree.ElementTree(root)
        return tree
    except etree.XMLSyntaxError as e: # Catch lxml specific parse error
        st.error(f"Error parsing {uploaded_file.name}: Invalid XML structure. {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while parsing {uploaded_file.name}: {e}")
        return None

# find_ids function remains largely the same, as lxml's API is similar for basic access
def find_ids(xml_data):
    """Finds potential defining IDs and referencing attributes in parsed XMLs."""
    found_definitions = {} # base_id -> {file_name, element}
    found_references = {} # base_id -> list of {file_name, element, attribute_name, prefix, original_value}

    for file_name, tree in xml_data.items():
        if tree is None: continue
        try:
            root = tree.getroot()
            # Use iter() which works for both lxml and ET
            for element in root.iter():
                # Skip comments and processing instructions if any were kept
                if not isinstance(element.tag, str):
                    continue

                element_tag = element.tag

                # --- Find Definitions (standard id attribute) ---
                element_id_val = element.get('id') # Use .get() for safer access
                if element_id_val: # Handles None or empty string
                    base_def_id = element_id_val # Use full ID as key for simplicity now

                    if base_def_id in found_definitions:
                        st.warning(f"Duplicate definition ID '{base_def_id}' found. Using first instance from '{found_definitions[base_def_id]['file_name']}'. Second instance in '{file_name}'.")
                    else:
                        found_definitions[base_def_id] = {'file_name': file_name, 'element': element}

                # --- Find References (based on REFERENCE_ATTRIBUTES) ---
                for attr_name, prefix_or_marker in REFERENCE_ATTRIBUTES.items():
                    original_value = element.get(attr_name)
                    if original_value: # Handles None or empty string
                        base_id = None
                        prefix = None
                        is_reference = False

                        if isinstance(prefix_or_marker, str) and prefix_or_marker.endswith('.'):
                            configured_prefix = prefix_or_marker
                            if original_value.startswith(configured_prefix):
                                prefix = configured_prefix
                                base_id = original_value[len(prefix):]
                                is_reference = True
                        elif prefix_or_marker == 'EQUIPMENT_ITEM_ID' and attr_name == 'id' and element_tag in ('Equipment', 'equipment'):
                            if original_value.startswith("Item."):
                                prefix = "Item."
                                base_id = original_value[len(prefix):]
                            else:
                                prefix = None
                                base_id = original_value
                            is_reference = True
                        elif prefix_or_marker == 'TEMPLATE_REFERENCE' and attr_name == 'name' and element_tag == 'template':
                             if '.' in original_value:
                                 parts = original_value.split('.', 1)
                                 if parts[0] and parts[0][0].isupper():
                                      prefix = parts[0] + "."
                                      base_id = parts[1]
                                      is_reference = True
                        elif prefix_or_marker is None and attr_name != 'id':
                             if '.' in original_value:
                                 parts = original_value.split('.', 1)
                                 if parts[0] and parts[0][0].isupper() and len(parts[0]) > 1:
                                      prefix = parts[0] + "."
                                      base_id = parts[1]
                                      is_reference = True

                        if is_reference and base_id:
                            if base_id not in found_references:
                                found_references[base_id] = []
                            # Store reference info (element itself is needed)
                            found_references[base_id].append({
                                'file_name': file_name,
                                'element': element,
                                'attribute_name': attr_name,
                                'prefix': prefix,
                                'original_value': original_value
                            })
        except Exception as e:
             st.error(f"Error iterating elements in {file_name}: {e}")

    return found_definitions, found_references


# perform_refactor remains largely the same logic
def perform_refactor(old_base_id, new_base_id, xml_data, definitions, references):
    """Performs the refactoring across all loaded XML data using BASE IDs."""
    changes_made = []
    processed_elements = set() # Track (file_name, element_identity, attribute_name)

    # --- 1. Update Definition ---
    definition_updated = False
    definition_key_found = None
    if old_base_id in definitions: definition_key_found = old_base_id
    else:
        for def_id_key in definitions.keys():
            if '.' in def_id_key and def_id_key.split('.', 1)[1] == old_base_id:
                definition_key_found = def_id_key; break

    if definition_key_found:
        def_info = definitions[definition_key_found]
        def_file = def_info['file_name']
        def_element = def_info['element']
        # Use element itself for identity with lxml (more reliable than id())
        element_id_tuple = (def_file, def_element, 'id')

        if element_id_tuple not in processed_elements:
            try:
                current_def_id = def_element.get('id') # Use .get()
                if current_def_id == definition_key_found:
                    new_def_id = new_base_id
                    if '.' in definition_key_found:
                        prefix_part = definition_key_found.split('.', 1)[0] + "."
                        new_def_id = prefix_part + new_base_id
                    def_element.set('id', new_def_id) # Use .set()
                    changes_made.append(f"DEFINED: In '{def_file}', changed ID '{current_def_id}' to '{new_def_id}' for tag '{def_element.tag}'.")
                    processed_elements.add(element_id_tuple)
                    definition_updated = True
                else:
                    changes_made.append(f"WARNING: Definition element ID mismatch in '{def_file}'. Expected '{definition_key_found}', found '{current_def_id}'. No change.")
            except Exception as e: st.error(f"Error updating definition for {definition_key_found} in {def_file}: {e}")

    if not definition_updated and not definition_key_found:
        changes_made.append(f"WARNING: Definition for base ID '{old_base_id}' not found.")

    # --- 2. Update Specific References ---
    if old_base_id in references:
        for ref_info in references[old_base_id]:
            ref_file, ref_element, ref_attr_name = ref_info['file_name'], ref_info['element'], ref_info['attribute_name']
            ref_prefix, original_value = ref_info.get('prefix'), ref_info['original_value']
            element_id_tuple = (ref_file, ref_element, ref_attr_name)
            if element_id_tuple in processed_elements: continue

            current_value = ref_element.get(ref_attr_name)
            if current_value == original_value:
                expected_old_value = f"{ref_prefix or ''}{old_base_id}"
                if original_value == expected_old_value:
                    try:
                        new_value_with_prefix = f"{ref_prefix or ''}{new_base_id}"
                        ref_element.set(ref_attr_name, new_value_with_prefix) # Use .set()
                        changes_made.append(f"REFERENCED ({ref_attr_name}): In '{ref_file}', changed '{original_value}' to '{new_value_with_prefix}' for tag '{ref_element.tag}'.")
                        processed_elements.add(element_id_tuple)
                    except Exception as e: st.error(f"Error updating ref for {old_base_id} in {ref_file} attr '{ref_attr_name}': {e}")
                else:
                    changes_made.append(f"INFO: Ref in '{ref_file}' ({ref_attr_name}='{original_value}') skipped. Value != expected pattern '{expected_old_value}'.")
                    processed_elements.add(element_id_tuple)
            else:
                changes_made.append(f"WARNING: Ref in '{ref_file}' ({ref_attr_name}) skipped. Expected '{original_value}', found '{current_value}'.")
                processed_elements.add(element_id_tuple)

    # --- 3. Broader Search (Fallback) ---
    st.write("Performing broader reference search across all attributes (fallback)...")
    broad_changes = 0
    for file_name, tree in xml_data.items():
         if tree is None: continue
         root = tree.getroot()
         for element in root.iter():
             if not isinstance(element.tag, str): continue # Skip comments/PIs
             # Need to use .attrib directly here if modifying during iteration isn't safe
             # Lxml .attrib is a dict-like proxy, safer to iterate keys then get/set
             current_attrs = dict(element.attrib) # Create copy
             for attr_name, attr_value in current_attrs.items():
                 element_id_tuple = (file_name, element, attr_name)
                 if element_id_tuple in processed_elements: continue

                 potential_prefix, value_matches, expected_new = None, False, None
                 if '.' in attr_value:
                     parts = attr_value.split('.', 1)
                     if parts[0] and parts[0][0].isupper() and parts[1] == old_base_id:
                          potential_prefix, value_matches = parts[0] + ".", True
                          expected_new = f"{potential_prefix}{new_base_id}"
                 elif attr_value == old_base_id:
                     is_likely = attr_name in REFERENCE_ATTRIBUTES or \
                                 (element.tag in ('Equipment', 'equipment') and attr_name == 'id') or \
                                 (element.tag == 'template' and attr_name == 'name')
                     if is_likely:
                          potential_prefix, value_matches, expected_new = None, True, new_base_id

                 if value_matches and expected_new is not None:
                     try:
                         element.set(attr_name, expected_new) # Use .set()
                         changes_made.append(f"REFERENCED (broad/{attr_name}): In '{file_name}', changed '{attr_value}' to '{expected_new}' for tag '{element.tag}'.")
                         processed_elements.add(element_id_tuple)
                         broad_changes += 1
                     except Exception as e: st.error(f"Error updating broad ref for {old_base_id} in {file_name} attr '{attr_name}': {e}")

    st.write(f"Broader search finished. Found {broad_changes} potential broad references.")
    return changes_made


# Use lxml for creating the zip with pretty printing
def create_zip(xml_data):
    """Creates a zip file in memory containing the modified XML data using lxml."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, tree in xml_data.items():
            if tree:
                try:
                    # Use lxml.etree.tostring for pretty printing
                    xml_bytes = etree.tostring(
                        tree,
                        pretty_print=True,      # <<< THE KEY CHANGE FOR FORMATTING
                        xml_declaration=True,   # Add <?xml...> declaration
                        encoding='utf-8'        # Specify encoding
                    )
                    zip_file.writestr(file_name, xml_bytes)
                except Exception as e:
                    st.error(f"Error serializing or writing {file_name} to zip: {e}")
            else:
                 st.warning(f"Skipping file '{file_name}' for ZIP creation (not parsed correctly).")
    zip_buffer.seek(0)
    return zip_buffer

# --- UI Helper ---
def get_element_path(element):
    """Helper to create a simple path string for an element."""
    # Use lxml's .get method
    elem_id = element.get('id')
    if elem_id:
         return f"{element.tag}[id={elem_id}]"
    return element.tag

# --- Streamlit App ---
# (The Streamlit UI part remains largely the same, just ensure it uses
#  the variables/functions modified above correctly)
st.set_page_config(layout="wide")

st.title("Bannerlord Mod XML ID Refactor Tool (Attribute-Focused)")
st.warning("⚠️ **Prototype Limitations:** Basic ID detection. No pattern renaming. **Backup files!** Uses lxml for formatting.")

# --- Session State Initialization ---
default_state = {
    'uploaded_files_data': {}, 'parsed_xml_data': {}, 'definitions': {},
    'references': {}, 'primary_file': None, 'selected_attribute_key': None,
    'selected_ref_info': None, 'new_id_input_value': "",
    'refactor_results': [], 'show_download': False
}
for key, value in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- File Uploader ---
uploaded_files = st.file_uploader(
    "Upload ALL relevant XML files (incl. spcultures.xml)", type=['xml'],
    accept_multiple_files=True, key="file_uploader",
    help="Select spcultures.xml and files defining/referencing IDs (troops, characters, etc.)"
)

# --- Main Logic ---
if uploaded_files:
    new_file_names = set(f.name for f in uploaded_files)
    cached_file_names = set(st.session_state.get('uploaded_files_data', {}).keys())

    if new_file_names != cached_file_names:
        st.info(f"New file upload detected ({len(uploaded_files)} files). Reprocessing...")
        current_uploaded_data = {f.name: f for f in uploaded_files}
        st.session_state.uploaded_files_data = current_uploaded_data
        for key in default_state:
            if key != 'uploaded_files_data': st.session_state[key] = default_state[key]

        with st.spinner(f"Processing {len(uploaded_files)} files..."):
            temp_parsed_data = {}
            files_processed_count, files_failed_count = 0, 0
            for file_name, uploaded_file_obj in current_uploaded_data.items():
                 parsed_tree = parse_xml(uploaded_file_obj) # Calls the lxml version
                 temp_parsed_data[file_name] = parsed_tree
                 if parsed_tree: files_processed_count += 1
                 else: files_failed_count += 1
            st.session_state.parsed_xml_data = temp_parsed_data

            if files_processed_count > 0:
                st.session_state.definitions, st.session_state.references = find_ids(st.session_state.parsed_xml_data)
                st.success(f"Processed {files_processed_count} files. Found global definitions/references.")
                if files_failed_count > 0: st.warning(f"{files_failed_count} files failed to parse.")
                valid_files = [name for name, tree in st.session_state.parsed_xml_data.items() if tree]
                if "spcultures.xml" in valid_files: st.session_state.primary_file = "spcultures.xml"
                elif valid_files: st.session_state.primary_file = valid_files[0]
            elif files_failed_count > 0: st.error("All uploaded files failed to parse.")
        st.rerun()

    has_valid_data = any(tree for tree in st.session_state.get('parsed_xml_data', {}).values())
    if not has_valid_data:
        if st.session_state.get('uploaded_files_data'): st.error("XML data could not be parsed.")
    else:
        parsed_file_names = [name for name, tree in st.session_state.parsed_xml_data.items() if tree]
        if not parsed_file_names: st.warning("No files parsed successfully.")
        else:
            if st.session_state.primary_file not in parsed_file_names: st.session_state.primary_file = parsed_file_names[0]
            selected_primary_file = st.selectbox("Select primary file to browse:", parsed_file_names, index=parsed_file_names.index(st.session_state.primary_file), key="primary_file_selector")
            if selected_primary_file != st.session_state.primary_file:
                st.session_state.primary_file = selected_primary_file
                st.session_state.selected_attribute_key, st.session_state.selected_ref_info, st.session_state.new_id_input_value = None, None, ""
                st.rerun()

            st.subheader(f"Select Attribute to Refactor in '{st.session_state.primary_file}'")
            attribute_options = {"<Select an attribute>": None}
            primary_tree = st.session_state.parsed_xml_data.get(st.session_state.primary_file)
            if primary_tree:
                try:
                    root = primary_tree.getroot()
                    count = 0
                    for element in root.iter():
                        if not isinstance(element.tag, str): continue # Skip comments/PIs
                        elem_path_str = get_element_path(element)
                        for attr_name, original_value in element.attrib.items(): # Use element.attrib with lxml
                            if not original_value: continue
                            prefix_or_marker = REFERENCE_ATTRIBUTES.get(attr_name)
                            base_id, prefix, is_reference = None, None, False
                            # Reference detection logic (same as before)
                            if isinstance(prefix_or_marker, str) and prefix_or_marker.endswith('.'):
                                if original_value.startswith(prefix_or_marker): prefix, base_id, is_reference = prefix_or_marker, original_value[len(prefix_or_marker):], True
                            elif prefix_or_marker == 'EQUIPMENT_ITEM_ID' and attr_name == 'id' and element.tag in ('Equipment', 'equipment'):
                                if original_value.startswith("Item."): prefix, base_id = "Item.", original_value[5:]
                                else: prefix, base_id = None, original_value
                                is_reference = True
                            elif prefix_or_marker == 'TEMPLATE_REFERENCE' and attr_name == 'name' and element.tag == 'template':
                                 if '.' in original_value:
                                     parts = original_value.split('.', 1)
                                     if parts[0] and parts[0][0].isupper(): prefix, base_id, is_reference = parts[0] + ".", parts[1], True
                            elif prefix_or_marker is None and attr_name != 'id':
                                 if '.' in original_value:
                                     parts = original_value.split('.', 1)
                                     if parts[0] and parts[0][0].isupper() and len(parts[0]) > 1: prefix, base_id, is_reference = parts[0] + ".", parts[1], True
                            # Add option if it's a reference
                            if is_reference and base_id:
                                display_text = f'{elem_path_str} | {attr_name}="{original_value}"'
                                option_key = f"{st.session_state.primary_file}-{count}"
                                attribute_options[display_text] = {
                                    "key": option_key, "file": st.session_state.primary_file,
                                    "element_repr": elem_path_str, "attribute_name": attr_name,
                                    "original_value": original_value, "old_id": base_id, "prefix": prefix
                                }
                                count += 1
                except Exception as e: st.error(f"Error iterating elements in {st.session_state.primary_file}: {e}")

            if len(attribute_options) <= 1: st.info(f"No potential ID references found in '{st.session_state.primary_file}'.")
            else:
                 option_keys = list(attribute_options.keys())
                 current_attr_index = 0
                 if st.session_state.selected_attribute_key:
                      try: current_attr_index = next(i for i, k in enumerate(option_keys) if attribute_options[k] and attribute_options[k]['key'] == st.session_state.selected_attribute_key)
                      except (StopIteration, ValueError): current_attr_index = 0
                 selected_attr_display = st.selectbox("Select attribute to modify:", option_keys, index=current_attr_index, key="attribute_selector")
                 selected_info = attribute_options.get(selected_attr_display)
                 if selected_info: st.session_state.selected_attribute_key, st.session_state.selected_ref_info = selected_info['key'], selected_info
                 else: st.session_state.selected_attribute_key, st.session_state.selected_ref_info = None, None

                 if st.session_state.selected_ref_info:
                     ref_info = st.session_state.selected_ref_info
                     st.write(f"**Selected:** Attribute `{ref_info['attribute_name']}` = `{ref_info['original_value']}`")
                     st.write(f"(Element: `{ref_info['element_repr']}`, Base ID: `{ref_info['old_id']}`, Prefix: `{ref_info['prefix'] or '(None)'}`)")
                     new_id_input = st.text_input(f"Enter New Base ID for '{ref_info['old_id']}':", key="new_id_input", value=st.session_state.new_id_input_value)
                     st.session_state.new_id_input_value = new_id_input
                     if st.button("Refactor This Attribute Globally", key="refactor_button"):
                         new_base_id = st.session_state.new_id_input_value.strip()
                         old_base_id = ref_info['old_id']
                         if old_base_id and new_base_id and new_base_id != old_base_id:
                             with st.spinner("Preparing... Creating temporary copies."): # Copy logic remains same
                                 temp_parsed_data = {}
                                 copy_success = True
                                 source_data = st.session_state.parsed_xml_data
                                 for fname, tree in source_data.items():
                                      if tree:
                                           try:
                                                # Use lxml's tostring/fromstring for copying
                                                xml_string = etree.tostring(tree.getroot(), encoding='utf-8')
                                                temp_root = etree.fromstring(xml_string)
                                                temp_parsed_data[fname] = etree.ElementTree(temp_root)
                                           except Exception as e: st.error(f"Error copying {fname}: {e}"); copy_success = False; temp_parsed_data[fname]=None
                                      else: temp_parsed_data[fname]=None
                             if not copy_success: st.error("Copying failed. Aborting.")
                             else:
                                 with st.spinner("Analyzing copies..."): temp_definitions, temp_references = find_ids(temp_parsed_data) # Uses lxml elements
                                 with st.spinner(f"Refactoring '{old_base_id}' to '{new_base_id}' globally..."):
                                     st.session_state.refactor_results = perform_refactor(old_base_id, new_base_id, temp_parsed_data, temp_definitions, temp_references) # Uses lxml elements
                                 st.session_state.parsed_xml_data = temp_parsed_data
                                 st.session_state.show_download = True
                                 st.success(f"Refactoring triggered by '{ref_info['attribute_name']}' complete.")
                                 st.session_state.definitions, st.session_state.references = find_ids(st.session_state.parsed_xml_data)
                                 st.session_state.selected_attribute_key, st.session_state.selected_ref_info, st.session_state.new_id_input_value = None, None, ""
                                 st.rerun()
                         elif not new_base_id: st.warning("Please enter a New ID.")
                         elif new_base_id == old_base_id: st.warning("New ID cannot be the same as the Old ID.")

    if st.session_state.refactor_results:
         st.subheader("Refactoring Summary:")
         st.text_area("Changes Made:", "\n".join(st.session_state.refactor_results), height=300, key="results_area")
    if st.session_state.show_download:
         st.subheader("Download Modified Files")
         valid_xml_data = {name: tree for name, tree in st.session_state.get('parsed_xml_data', {}).items() if tree}
         if valid_xml_data:
             try:
                  zip_buffer = create_zip(valid_xml_data) # Calls the lxml version
                  st.download_button("Download Modified Files as ZIP", zip_buffer, "refactored_xml_files.zip", "application/zip", key="download_button")
                  st.info("Download ZIP and replace original files (after backup!).")
             except Exception as e: st.error(f"Error creating ZIP: {e}"); st.exception(e)
         else: st.warning("No valid XML data to download.")

elif not uploaded_files:
     if not st.session_state.get('parsed_xml_data'): st.info("Please upload XML files to begin.")
     if st.session_state.get('uploaded_files_data'):
          st.info("File selection cleared. Resetting state.")
          for key in default_state: st.session_state[key] = default_state[key]
          st.rerun()