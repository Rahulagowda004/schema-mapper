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
    .sample-case-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        background-color: #f8f9fa;
    }
    .sample-case-title {
        font-weight: bold;
        color: #333;
        margin-bottom: 4px;
    }
    .sample-case-desc {
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

def load_sample_data(case_number):
    """Load sample test case data"""
    testcases_dir = Path("testcases")
    
    if case_number == 1:
        # Academic Paper Citation
        passage_file = testcases_dir / "test case 1" / "NIPS-2017-attention-is-all-you-need-Bibtex.txt"
        schema_file = testcases_dir / "test case 1" / "paper citations_schema.json"
    elif case_number == 2:
        # GitHub Actions
        passage_file = testcases_dir / "test case 2" / "github actions sample input.txt"
        schema_file = testcases_dir / "test case 2" / "github_actions_schema.json"
    elif case_number == 3:
        # Resume
        passage_file = testcases_dir / "test case 3" / "resume.txt"
        schema_file = testcases_dir / "test case 3" / "convert your resume to this schema.json"
    else:
        return None, None
    
    try:
        if passage_file.exists() and schema_file.exists():
            with open(passage_file, 'r', encoding='utf-8') as f:
                passage_content = f.read()
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_content = json.load(f)
            return passage_content, schema_content
    except Exception as e:
        st.error(f"Error loading sample case: {e}")
    
    return None, None

def main():
    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'sample_loaded' not in st.session_state:
        st.session_state.sample_loaded = False
    if 'passage_content' not in st.session_state:
        st.session_state.passage_content = ""
    if 'schema_content' not in st.session_state:
        st.session_state.schema_content = {}
    
    # Title
    st.title("🗂️ Schema Mapper")
    
    # Sample test cases section in main area
    st.subheader("🧪 Sample Test Cases")
    st.markdown("Try these pre-built examples:")
    
    # Sample case buttons in columns
    sample_cases = [
        {
            "number": 1,
            "title": "📚 Academic Paper Citation",
            "description": "Convert BibTeX citation to structured JSON"
        },
        {
            "number": 2,
            "title": "⚙️ GitHub Actions Workflow",
            "description": "Generate GitHub Actions YAML from description"
        },
        {
            "number": 3,
            "title": "👤 Resume Parser",
            "description": "Structure resume data into JSON format"
        }
    ]
    
    # Create three columns for sample cases
    case_col1, case_col2, case_col3 = st.columns(3)
    
    for i, case in enumerate(sample_cases):
        with [case_col1, case_col2, case_col3][i]:
            st.markdown(f"""
            <div class="sample-case-card">
                <div class="sample-case-title">{case['title']}</div>
                <div class="sample-case-desc">{case['description']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Load Case {case['number']}", key=f"sample_{case['number']}", use_container_width=True):
                passage_content, schema_content = load_sample_data(case['number'])
                if passage_content and schema_content:
                    st.session_state.passage_content = passage_content
                    st.session_state.schema_content = schema_content
                    st.session_state.sample_loaded = True
                    st.session_state.result = None  # Clear previous results
                    st.success(f"✅ Loaded {case['title']}")
                    st.rerun()
                else:
                    st.error("❌ Failed to load sample case")
    
    # Clear sample data button
    if st.session_state.sample_loaded:
        if st.button("🗑️ Clear Sample Data", use_container_width=False):
            st.session_state.passage_content = ""
            st.session_state.schema_content = {}
            st.session_state.sample_loaded = False
            st.session_state.result = None
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar for file uploads
    st.sidebar.header("� File Upload")
    
    # Passage file upload in sidebar
    st.sidebar.subheader("📄 Passage File")
    passage_file = st.sidebar.file_uploader("Upload text file", type=['txt'], key="passage_upload")
    
    # Schema file upload in sidebar  
    st.sidebar.subheader("📋 Schema File")
    schema_file = st.sidebar.file_uploader("Upload JSON schema", type=['json'], key="schema_upload")
    
    # Handle file uploads
    if passage_file:
        st.session_state.passage_content = passage_file.read().decode('utf-8')
        st.session_state.sample_loaded = False
    
    if schema_file:
        st.session_state.schema_content = json.loads(schema_file.read().decode('utf-8'))
        st.session_state.sample_loaded = False
    
    # Clear sample data button in sidebar (only show if sample is loaded)
    if st.session_state.sample_loaded:
        if st.sidebar.button("🗑️ Clear Sample Data", use_container_width=True):
            st.session_state.passage_content = ""
            st.session_state.schema_content = {}
            st.session_state.sample_loaded = False
            st.session_state.result = None
            st.rerun()
    

    
    # Main content area - Create two columns
    col1, col2 = st.columns(2)
    
    # Column 1: File previews (stacked)
    with col1:
        # Passage Preview in first row
        st.header("📄 Passage Preview")
        if st.session_state.passage_content:
            st.text_area("Passage Content", value=st.session_state.passage_content, height=200, disabled=True)
        else:
            st.info("📤 Upload a passage file or load a sample case")
        
        # Schema Preview in second row
        st.header("📋 Schema Preview") 
        if st.session_state.schema_content:
            st.text_area("Schema Content", value=json.dumps(st.session_state.schema_content, indent=2), height=200, disabled=True)
        else:
            st.info("📤 Upload a schema file or load a sample case")
    
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
        if st.session_state.passage_content and st.session_state.schema_content:
            with st.spinner("Processing..."):
                # Create temp files
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_passage:
                    temp_passage.write(st.session_state.passage_content)
                    temp_passage_path = Path(temp_passage.name)
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_schema:
                    json.dump(st.session_state.schema_content, temp_schema)
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
            st.warning("⚠️ Please upload both files or load a sample case")
    
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