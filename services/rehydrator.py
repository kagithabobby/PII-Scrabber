SENSITIVE = {"AADHAAR", "PAN", "PIN", "PHONE"}

def safe_rehydrate(text, mapping):
    for placeholder, value in mapping.items():
        label = placeholder.split("_")[0].replace("[", "")

        if label in SENSITIVE:
            continue  # ❌ do not restore

        text = text.replace(placeholder, value)

    return text