import json
import os
from pathlib import Path

import requests
from pymed import PubMed

# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="PolyMind")

# Read config
script_dir = Path(os.path.abspath(__file__)).parent
conf_path = script_dir / "config.json"
with open(conf_path, "r") as config_file:
    config = json.load(config_file)
max_results = config.get("max_results", 5)
ctx_alloc = config.get("ctx_alloc", 0.3)


def main(params, memory, infer, ip, Shared_vars):
    # Definitions for API-based tokenization
    API_ENDPOINT_URL = Shared_vars.API_ENDPOINT_URI
    if Shared_vars.TABBY:
        API_ENDPOINT_URL += "v1/completions"
    else:
        API_ENDPOINT_URL += "completion"

    def tokenize(input):
        payload = {
            "add_bos_token": "true",
            "encode_special_tokens": "true",
            "decode_special_tokens": "true",
            "text": input,
            "content": input,
        }
        request = requests.post(
            API_ENDPOINT_URL.replace("completions", "token/encode")
            if Shared_vars.TABBY
            else API_ENDPOINT_URL.replace("completion", "tokenize"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {Shared_vars.API_KEY}",
            },
            json=payload,
            timeout=360,
        )
        return (
            request.json()["length"]
            if Shared_vars.TABBY
            else len(request.json()["tokens"])
        )

    # Create a GraphQL query in plain text
    category = params.get("category")
    keywords = params.get("keywords")
    kw_chunked = keywords.split(",")
    query = ""

    if category.lower() == "therapy":
        query += "(Therapy/Broad[filter])"
    elif category.lower() == "diagnosis":
        query += "(Diagnosis/Broad[filter])"
    elif category.lower() == "etiology":
        query += "(Etiology/Broad[filter])"
    elif category.lower() == "prognosis":
        query += "(Prognosis/Broad[filter])"
    elif category.lower() == "clinical prediction guides":
        query += "(Clinical Prediction Guides/Broad[filter])"

    for chunk in kw_chunked:
        if len(query) > 0:
            query = f'{query} AND "{chunk.strip()}"[tw]'
        else:
            query = f'"{chunk.strip()}"[tw]'

    query = f'{query} AND medline[sb] AND "has abstract"[filter]'

    # Execute the query against the API
    results = pubmed.query(query, max_results=max_results)

    # Create message containing RAG content
    message = ""
    test_message = ""
    for article in results:
        text = ""
        r = article.toDict()

        if r.get("title"):
            text = text + r.get("title") + "\n"
        if r.get("pubmed_id"):
            text = (
                text
                + "URL: https://pubmed.ncbi.nlm.nih.gov/"
                + r.get("pubmed_id").split("\n")[0]
                + "/\n"
            )
        if r.get("publication_date"):
            text = text + "Publication Date: " + str(r.get("publication_date")) + "\n"
        if r.get("journal"):
            text = text + "Journal: " + r.get("journal") + "\n"
        if r.get("doi"):
            text = text + "DOI: " + r.get("doi").split("\n")[0] + "\n"
        if r.get("abstract"):
            text = text + r.get("abstract") + "\n"
        # if r.get("methods"):
        #    text = text + "Methods: " + r.get("methods") + "\n"
        # if r.get("results"):
        #    text = text + "Results: " + r.get("results") + "\n"
        # if r.get("conclusions"):
        #    text = text + "Conclusions: " + r.get("conclusions") + "\n"

        # Add separator if this is the first result
        if len(message) > 0:
            test_message = message + "***\n"
        test_message += text

        # Prevent RAG content from taking up too much of the context
        if tokenize(test_message) < (Shared_vars.config.ctxlen * ctx_alloc):
            message = test_message
        else:
            break

    # Handle unsuccessful search
    if len(message) == 0:
        print("No results from PubMed")
        return "No search results found on PubMed, notify the user of this and respond based on your knowledge"

    print(message)
    return "<search_results>:\n" + message + "</search_results>"


if __name__ == "__main__":
    main(params, memory, infer, ip, Shared_vars)
