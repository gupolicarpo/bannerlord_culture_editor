import streamlit as st
import xml.etree.ElementTree as ET
import zipfile
from xml.dom import minidom

# Function to parse XML files
def load_xml(file):
    try:
        tree = ET.parse(file)
        return tree
    except ET.ParseError as e:
        st.error(f"Error parsing {file.name}: {e}")
        return None

# Function to update IDs in XML
def update_ids(tree, old_culture_id, new_culture_id, npc_mappings):
    root = tree.getroot()
    for elem in root.iter():
        for attr in elem.attrib:
            if elem.attrib[attr] == f"Culture.{old_culture_id}":
                elem.set(attr, f"Culture.{new_culture_id}")
            elif elem.attrib[attr] == old_culture_id:
                elem.set(attr, new_culture_id)
            elif elem.attrib[attr] in npc_mappings:
                elem.set(attr, npc_mappings[elem.attrib[attr]])
    return tree

# Function to pretty-print XML with line breaks and indentation
def pretty_print_xml(tree):
    xml_str = ET.tostring(tree.getroot(), encoding="utf-8", method="xml")
    reparsed = minidom.parseString(xml_str)
    return reparsed.toprettyxml(indent="    ")

# Streamlit UI
st.title("XML Editor for Culture & NPC IDs")

uploaded_files = st.file_uploader("Upload XML files", accept_multiple_files=True)

if uploaded_files:
    # Load the XML files
    xml_trees = {file.name: load_xml(file) for file in uploaded_files}

    # Debug: Check uploaded files
    st.write("Uploaded files:", [file.name for file in uploaded_files])

    # Load spcultures.xml to get culture IDs
    spcultures = xml_trees.get("spcultures_vlandia.xml")  # Ensure correct file name
    if spcultures:
        root = spcultures.getroot()
        culture_ids = [c.get("id") for c in root.findall("Culture")]

        # Debug: Check culture IDs
        st.write("Culture IDs found:", culture_ids)

        # Culture selection dropdown
        selected_culture = st.selectbox("Select Culture ID:", culture_ids)
        new_culture_id = st.text_input("New Culture ID:", selected_culture)

        # Get NPCs linked to the selected culture
        npc_mappings = {}
        for culture in root.findall("Culture"):
            if culture.get("id") == selected_culture:
                for attr, value in culture.attrib.items():
                    if "NPCCharacter" in value:
                        new_value = st.text_input(f"Rename {value}:", value)
                        npc_mappings[value] = new_value

        # Debug: Show NPC mappings
        st.write("NPC Mappings for selected culture:", npc_mappings)

        # Apply changes
        if st.button("Apply Changes"):
            for file_name, tree in xml_trees.items():
                xml_trees[file_name] = update_ids(tree, selected_culture, new_culture_id, npc_mappings)

            st.success("Changes applied!")

            # Save updated XMLs in a zip file
            with zipfile.ZipFile("modified_xmls.zip", "w") as zipf:
                for file_name, tree in xml_trees.items():
                    tree.write(file_name, encoding="utf-8")
                    zipf.write(file_name)

            with open("modified_xmls.zip", "rb") as f:
                st.download_button("Download Modified XMLs", f, "modified_xmls.zip")

        # Show pretty-printed XML of the first uploaded file
        if uploaded_files:
            st.subheader("Pretty-Printed XML Output")
            pretty_xml = pretty_print_xml(spcultures)
            st.code(pretty_xml, language="xml")
