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

def main():
    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    
    # Title
    st.title("🗂️ Schema Mapper")
    
    # File uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📄 Passage File")
        passage_file = st.file_uploader("Upload text file", type=['txt'])
        
        if passage_file:
            passage_content = passage_file.read().decode('utf-8')
            st.text_area("Preview", value=passage_content, height=300, disabled=True)
    
    with col2:
        st.header("📋 Schema File")
        schema_file = st.file_uploader("Upload JSON schema", type=['json'])
        
        if schema_file:
            schema_content = json.loads(schema_file.read().decode('utf-8'))
            st.json(schema_content)
    
    # Generate button
    if st.button("Generate JSON", type="primary"):
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
                else:
                    st.error("❌ Failed to generate JSON")
        else:
            st.warning("⚠️ Please upload both files")
    
    # Show result
    if st.session_state.result:
        st.header("📊 Result")
        
        # Format result
        if isinstance(st.session_state.result, str):
            try:
                result_dict = json.loads(st.session_state.result)
            except:
                result_dict = st.session_state.result
        else:
            result_dict = st.session_state.result
        
        formatted_json = json.dumps(result_dict, indent=2)
        
        # Display
        st.text_area("JSON Output", value=formatted_json, height=300)
        
        # Download button
        st.download_button(
            "💾 Download JSON",
            data=formatted_json,
            file_name="output.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()