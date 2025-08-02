# Cell 1 - Imports
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from logger import logging
from pathlib import Path
import json
import os

class SchemaMapper:
    def __init__(self):
        
        load_dotenv()
        
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT"), 
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.3,
            model_kwargs={"response_format": {"type": "json_object"}}
            )

        self.parser = JsonOutputParser()

        self.prompt = PromptTemplate(
            template = """
            You are a strict JSON generator. Your task is to:
            1. Carefully read the passage below.
            2. Analyze the given JSON Schema.
            3. Generate a valid JSON object using only the keys defined in the schema.
            4. Use correct data types as defined in the schema, including:
            - Only lowercase booleans (`true`, `false`)
            - No strings like `"true"` or `"false"`
            - No uppercase booleans (`True`, `False`)
            5. Do not include any extra keys or explanations. Return only valid and strict JSON output.
            6. Ensure that all values match their expected types, formats, and regular expressions as defined in the schema.

            **Passage**: {passage}

            **Schema**: {schema}

            **Output**: (Only return the JSON. No markdown, no comments, no extra text.)

            {format_instruction}
            """,
            input_variables=["passage","schema"],
            partial_variables={"format_instruction": self.parser.get_format_instructions()},
        )

        self.chain = self.prompt | self.llm | self.parser

    def json_generator(self, passage:Path, schema:Path)->dict:
        try:
            with open (passage, "r") as file:
                passage_content = file.read()
                logging.info("Passage content loaded successfully.")
                
            with open (schema, "r") as file:
                schema_content = json.load(file)
                logging.info("Schema content loaded successfully.")

            logging.info("Generating JSON initialized")
            result = json.dumps(self.chain.invoke({"passage": passage_content,"schema":json.dumps(schema_content)}))
            logging.info("Generating JSON completed")
            
            return result
    
        except Exception as e:
            logging.error(f"Error in json_generator: {e}")
            return None

if __name__ == "__main__":
    mapper = SchemaMapper()
    result = mapper.json_generator(passage=Path("testcases/test case 3/resume.txt"), schema=Path("testcases/test case 3/convert your resume to this schema.json"))
    print(result)