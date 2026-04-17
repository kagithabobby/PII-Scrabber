def rehydrate(text, mapping):
    for placeholder, real_value in mapping.items():
        text = text.replace(placeholder, real_value)
    return text