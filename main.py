from pymed import PubMed

# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="PolyMind")


def main(params, memory, infer, ip, Shared_vars):
    # Create a GraphQL query in plain text
    keywords = params.get("keywords")
    kw_chunked = keywords.split(",")
    query = ""

    for chunk in kw_chunked:
        if len(query) > 0:
            query = f'{query} AND "{chunk.strip()}"[tw]'
        else:
            query = f'"{chunk.strip()}"[tw]'

    query = f'{query} AND medline[sb] AND "has abstract"[filter]'

    # Execute the query against the API
    results = pubmed.query(query, max_results=10)

    # Create message containing RAG content
    message = ""
    for article in results:
        text = ""
        r = article.toDict()

        if r.get("title"):
            text = text + r.get("title") + "\n"
        # if r.get("pubmed_id"):
        #    text = (
        #        text
        #        + "URL: https://pubmed.ncbi.nlm.nih.gov/"
        #        + r.get("pubmed_id")
        #        + "/\n"
        #    )
        if r.get("publication_date"):
            text = text + "Publication Date: " + str(r.get("publication_date")) + "\n"
        if r.get("journal"):
            text = text + "Journal: " + r.get("journal") + "\n"
        if r.get("doi"):
            text = text + "DOI: " + r.get("doi") + "\n"
        if r.get("abstract"):
            text = text + "Abstract: " + r.get("abstract") + "\n"
        # if r.get("methods"):
        #    text = text + "Methods: " + r.get("methods") + "\n"
        # if r.get("results"):
        #    text = text + "Results: " + r.get("results") + "\n"
        # if r.get("conclusions"):
        #    text = text + "Conclusions: " + r.get("conclusions") + "\n"

        if len(message) > 0:
            message += "***\n"
        message += text

    if len(message) == 0:
        return "No search results found on PubMed, notify the user of this and respond based on your knowledge"

    return "<search_results>:\n" + message + "</search_results>"


if __name__ == "__main__":
    main(params, memory, infer, ip, Shared_vars)
