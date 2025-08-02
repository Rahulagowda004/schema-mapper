import streamlit as st
import json
from pathlib import Path
import tempfile
import os
from main import SchemaMapper
from logger import logging

# Set page configuration
st.set_page_config(
    page_title="Schema Mapper",
    page_icon="🗂️",
    layout="wide"
)

# Add dark theme CSS
st.markdown("""
<style>
    .dark-json {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
    }
    .dark-json pre {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    .dark-json code {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    
    # Title
    st.title("🗂️ Schema Mapper")
    
    # Sidebar for file uploads and bookmarks
    st.sidebar.header("📁 File Upload")
    
    # Passage file upload in sidebar
    st.sidebar.subheader("📄 Passage File")
    passage_file = st.sidebar.file_uploader("Upload text file", type=['txt'], key="passage_upload")
    
    if passage_file:
        passage_content = passage_file.read().decode('utf-8')
    
    # Schema file upload in sidebar  
    st.sidebar.subheader("📋 Schema File")
    schema_file = st.sidebar.file_uploader("Upload JSON schema", type=['json'], key="schema_upload")
    
    if schema_file:
        schema_content = json.loads(schema_file.read().decode('utf-8'))
    

    
    # Main content area - Create two columns
    col1, col2 = st.columns(2)
    
    # Column 1: File previews (stacked)
    with col1:
        # Passage Preview in first row
        st.header("📄 Passage Preview")
        if passage_file:
            st.text_area("Passage Content", value=passage_content, height=200, disabled=True)
        else:
            st.info("� Upload a passage file in the sidebar")
        
        # Schema Preview in second row
        st.header("📋 Schema Preview") 
        if schema_file:
            st.text_area("Schema Content", value=json.dumps(schema_content, indent=2), height=200, disabled=True)
        else:
            st.info("� Upload a schema file in the sidebar")
    
    # Add some spacing
    st.write("")
    
    # Create two columns for buttons side by side
    btn_col1, btn_col2 = st.columns(2)
    
    # Generate button in first column
    with btn_col1:
        generate_clicked = st.button("🧩 Generate JSON", type="primary", use_container_width=True)
    
    # Download button in second column (only active when result exists)
    with btn_col2:
        if st.session_state.result:
            # Format result for download
            if isinstance(st.session_state.result, str):
                try:
                    download_data = json.loads(st.session_state.result)
                except:
                    download_data = st.session_state.result
            else:
                download_data = st.session_state.result
            
            formatted_download = json.dumps(download_data, indent=2)
            
            st.download_button(
                "💾 Download JSON",
                data=formatted_download,
                file_name="output.json",
                mime="application/json",
                use_container_width=True,
                key="download_button"
            )
        else:
            # Empty space when no result - no placeholder button
            st.write("")
    
    # Handle generate button click
    if generate_clicked:
            if passage_file and schema_file:
                with st.spinner("Processing..."):
                    # Create temp files
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_passage:
                        temp_passage.write(passage_content)
                        temp_passage_path = Path(temp_passage.name)
                    
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_schema:
                        json.dump(schema_content, temp_schema)
                        temp_schema_path = Path(temp_schema.name)
                    
                    # Generate JSON
                    mapper = SchemaMapper()
                    result = mapper.json_generator(temp_passage_path, temp_schema_path)
                    
                    # Clean up
                    os.unlink(temp_passage_path)
                    os.unlink(temp_schema_path)
                    
                    if result:
                        st.session_state.result = result
                        st.success("✅ JSON generated successfully!")
                        st.rerun()  # Refresh to show download button
                    else:
                        st.error("❌ Failed to generate JSON")
            else:
                st.warning("⚠️ Please upload both files")
    
    # Show result in column 2
    with col2:
        st.header("📊 Result")
        
        if st.session_state.result:
            # Format result
            if isinstance(st.session_state.result, str):
                try:
                    result_dict = json.loads(st.session_state.result)
                except:
                    result_dict = st.session_state.result
            else:
                result_dict = st.session_state.result
            
            formatted_json = json.dumps(result_dict, indent=2)
            
            # Display JSON with styling
            st.text_area("JSON Output", value=formatted_json, height=493, help="Generated JSON output based on your schema")
        else:
            st.info("Click 'Generate JSON' to see the result here")

if __name__ == "__main__":
    main()