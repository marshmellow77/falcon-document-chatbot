from langchain import PromptTemplate, LLMChain
from langchain.llms.sagemaker_endpoint import LLMContentHandler, SagemakerEndpoint
import json
from typing import Dict


prompt_template = "What is a good name for a company that makes {product}?"
endpoint_name = "falcon-40b-instruct-48xl"


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"
    len_prompt = 0

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        self.len_prompt = len(prompt)
        input_str = json.dumps({"inputs": prompt, "parameters": {"max_new_tokens": 50, "do_sample": False, "repetition_penalty": 1.1}})
        return input_str.encode('utf-8')

    def transform_output(self, output: bytes) -> str:
        response_json = output.read()
        res = json.loads(response_json)
        # ans = res[0]['generated_text']
        ans = res[0]['generated_text'][self.len_prompt:]
        return ans


content_handler = ContentHandler()
llm = SagemakerEndpoint(
        endpoint_name=endpoint_name,
        region_name="us-east-1",
        content_handler=content_handler,
        credentials_profile_name="default"
    )

llm_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(prompt_template)
)

print(llm_chain("colorful socks")["text"])
