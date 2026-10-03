def strip_wrapping_quotes(text):
    """Remove a matching pair of quotation marks around text.

    Handles trailing content (emojis, spaces) after the closing quote, which
    GPT-3.5 sometimes appends outside the wrapping quotes.
    """
    stripped_text = text.strip()
    quote_pairs = {'"': '"', "'": "'", '“': '”', '‘': '’'}

    if len(stripped_text) >= 2 and stripped_text[0] in quote_pairs:
        closing = quote_pairs[stripped_text[0]]
        closing_index = stripped_text.rfind(closing)
        if closing_index > 0:
            inner = stripped_text[1:closing_index]
            trailing = stripped_text[closing_index + 1:]
            return (inner + trailing).strip()

    return stripped_text
