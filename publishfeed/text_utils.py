def strip_wrapping_quotes(text):
    """Remove a matching pair of quotation marks around text."""
    stripped_text = text.strip()
    quote_pairs = {'"': '"', "'": "'", '“': '”', '‘': '’'}

    if len(stripped_text) >= 2 and stripped_text[0] in quote_pairs:
        if stripped_text[-1] == quote_pairs[stripped_text[0]]:
            return stripped_text[1:-1]

    return stripped_text
