def format_tokens(tokens):
    if tokens < 1000:
        return str(tokens)
    elif tokens < 1000000:
        return f"{tokens/1000:.1f}K"
    elif tokens < 1000000000:
        return f"{tokens/1000000:.1f}M"
    elif tokens < 1000000000000:
        return f"{tokens/1000000000:.1f}B"
    elif tokens < 1000000000000000:
        return f"{tokens/1000000000000:.1f}T"
    elif tokens < 1000000000000000000:
        return f"{tokens/1000000000000000:.1f}Q"
    elif tokens < 1000000000000000000000:
        return f"{tokens/1000000000000000000:.1f}S"
    elif tokens < 1000000000000000000000000:
        return f"{tokens/1000000000000000000000:.1f}O"
    elif tokens < 1000000000000000000000000000:
        return f"{tokens/1000000000000000000000000:.1f}N"
    elif tokens < 1000000000000000000000000000000:
        return f"{tokens/1000000000000000000000000000:.1f}D"