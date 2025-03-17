import streamlit as st
import xml.etree.ElementTree as ET
import zipfile
from xml.dom import minidom
import re

# Function to parse XML files
def load_xml(file):
    try:
        tree = ET.parse(file)
        return tree
    except ET.ParseError as e:
        st.error(f"Error parsing {file.name}: {e}")
        return None

# Function to update IDs in XML (also updates NPCs and other related entries)
def update_ids(tree, old_culture_id, new_culture_id, npc_mappings):
    root = tree.getroot()
    
    # Iterate over all elements and attributes to update references
    for elem in root.iter():
        # Update culture references in attributes
        for attr in elem.attrib:
            if elem.attrib[attr] == f"Culture.{old_culture_id}":
                elem.set(attr, f"Culture.{new_culture_id}")
            elif elem.attrib[attr] == old_culture_id:
                elem.set(attr, new_culture_id)
            elif elem.attrib[attr] in npc_mappings:
                elem.set(attr, npc_mappings[elem.attrib[attr]])

        # Additionally, check for NPC names within inner text (e.g., inside <name> tags)
        if elem.tag == "name" and "NPCCharacter" in elem.text:
            if elem.text in npc_mappings:
                elem.text = npc_mappings[elem.text]
    
    return tree

# Function to fix malformed XML content
def fix_malformed_xml(content: str) -> str:
    """Corrects common XML issues before formatting"""
    content = re.sub(r"<(\w+)<", r"<\1 ", content)  # Fix malformed opening tags
    content = re.sub(r'=\s*([^"\s]+)(\s|>)', r'="\1"\2', content)  # Add missing quotes
    content = re.sub(r"<(\w+)([^>]*)>", r"<\1\2>", content)  # Close unclosed tags
    return content

# Function to format XML with pretty printing and aligned attributes
def format_xml_string(xml_str: str) -> str:
    """Full XML formatting pipeline"""
    corrected = fix_malformed_xml(xml_str)  # Fix common issues
    parsed = minidom.parseString(corrected)
    pretty_xml = parsed.toprettyxml(indent="    ")
    
    # Step 3: Attribute alignment
    return re.sub(
        r"(<[\w:]+)(\s+[^>]*?)(/?>)", 
        lambda m: m.group(1) + "\n    " + "\n    ".join(
            re.findall(r'\b\w+=".*?"', m.group(2))
        ) + m.group(3),
        pretty_xml
    )

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
            pretty_xml = format_xml_string(ET.tostring(spcultures.getroot(), encoding="utf-8").decode("utf-8"))
            st.code(pretty_xml, language="xml")




