def split_name_by_character_type(s, camel=True):
    """
    splits an input string into parts by camel case pattern,
    underscores, acronyms, digits, etc.

    Example:

    ss = [None, "", "ab de fg", "ab   de fg", "ab:cd:ef",
          "number5", "fooBar", "foo200Bar", "ASFRules"]

    for s in ss:
        print(split_by_character_type(s))

    []
    []
    ['ab', ' ', 'de', ' ', 'fg']
    ['ab', '   ', 'de', ' ', 'fg']
    ['ab', ':', 'cd', ':', 'ef']
    ['number', '5']
    ['foo', 'Bar']
    ['foo', '200', 'Bar']
    ['ASF', 'Rules']

    :param s: input string
    :param camel: account for camel case if true
    :return: list of string parts
    """
    if not s:
        return []
    parts = []
    token_start = 0
    for pos in range(1, len(s)):
        if ((s[pos].islower() and s[pos-1].islower()) or
            (s[pos].isupper() and s[pos-1].isupper()) or
            (s[pos].isdigit() and s[pos-1].isdigit()) or
            (not s[pos].isalnum() and not s[pos-1].isalnum())):
            continue
        if camel and s[pos].islower() and s[pos-1].isupper():
            new_token_start = pos - 1
            if new_token_start != token_start:
                parts.append(s[token_start: new_token_start])
                token_start = new_token_start
        else:
            parts.append(s[token_start: pos])
            token_start = pos
    parts.append(s[token_start: len(s)])
    return parts
