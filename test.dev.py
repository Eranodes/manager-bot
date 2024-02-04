import re


def strip_emojis(input_string):
    # Define a regular expression pattern to match emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        flags=re.UNICODE,
    )
    # Replace emojis with an empty string
    return emoji_pattern.sub(r"", input_string)


# Test the function
input_string = "Hello! 😀 How are you? 🌟🚀"
print(strip_emojis(input_string))
