import re
from typing import Optional


class Member:
    name = ""
    display_name = ""


def validate_string(member: Member) -> Optional[str]:
    input_str:str = member.display_name

    # Remove leading symbols
    bad_chars:str = "!@#$%^&*()_+-=[]{}`~|;:,.<>?/'\"\\"
    cleaned_name: str = input_str.lstrip(bad_chars).strip()

    # Remove emojis
    cleaned_name: str = cleaned_name.encode("ascii", "ignore").decode("ascii").strip()

    # Check if only contains letters of the English alphabet
    no_symbols: str = "".join(c for c in cleaned_name if c not in bad_chars).strip()
    if re.match("^[a-zA-Z0-9 ]+$", no_symbols):
        if len(cleaned_name) <= 3:
            return member.name

        return cleaned_name
    
    return member.name


mem = Member()
mem.display_name = "! Iᴛᴢ Iɴᴠɪɴᴄɪʙʟᴇ"
mem.name = "4dwdda"

validated_string = validate_string(member=mem)
if validated_string:
    print("Validated string:", validated_string)
else:
    print("Invalid string.")
