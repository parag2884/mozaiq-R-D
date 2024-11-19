import os


def get_words(page, line):
    result = []
    for word in page.words:
        if _in_span(word, line.spans):
            result.append(word)
    return result


def _in_span(word, spans):
    for span in spans:
        if word.span.offset >= span.offset and (word.span.offset + word.span.length) <= (span.offset + span.length):
            return True
    return False


def analyze_layout():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeResult

    # Set endpoint and API key directly for R&D purposes
    endpoint = "https://mozaiqfr-westus2.cognitiveservices.azure.com/"
    key = "2a2f335cfe4447b6a4671901232c345e"

    # Initialize the DocumentIntelligenceClient
    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Specify the local PDF file path
    path_to_sample_document = r"C:/Users/parag.baheti/Desktop/MSForm-New/PDF/invoice.pdf"  # Replace with the actual file path

    # Analyze the local document
    with open(path_to_sample_document, "rb") as document:
        poller = document_intelligence_client.begin_analyze_document(
            model_id="prebuilt-layout",
            analyze_request=document  # Use `analyze_request` for local files
        )
    
    result: AnalyzeResult = poller.result()

    # Analyze whether the document contains handwritten content
    if result.styles and any(style.is_handwritten for style in result.styles):
        print("Document contains handwritten content")
    else:
        print("Document does not contain handwritten content")

    # Analyze pages
    for page in result.pages:
        print(f"----Analyzing layout from page #{page.page_number}----")
        print(f"Page width: {page.width}, height: {page.height}, unit: {page.unit}")

        # Analyze lines
        for line_idx, line in enumerate(page.lines):
            words = get_words(page, line)
            print(
                f"...Line #{line_idx} has {len(words)} words and text: '{line.content}' "
                f"within bounding polygon: {line.polygon}"
            )
            for word in words:
                print(f"......Word '{word.content}' with confidence {word.confidence}")

        # Analyze tables
        for table_idx, table in enumerate(page.tables):
            print(f"Table #{table_idx} has {table.row_count} rows and {table.column_count} columns")
            for cell in table.cells:
                print(f"...Cell[{cell.row_index}][{cell.column_index}] text: '{cell.content}'")

    print("Document analysis complete!")


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError

    try:
        analyze_layout()
    except HttpResponseError as error:
        print(f"An error occurred: {error}")
        raise
