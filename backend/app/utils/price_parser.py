import re


def parse_price(text: str):
    if not text:
        return None

    # usuń wszystko oprócz cyfr, kropek i przecinków
    cleaned = re.sub(r"[^\d.,]", "", text)

    if not cleaned:
        return None

    # 1.799,00
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")

    # 1799,00
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    try:
        return float(cleaned)
    except ValueError:
        return None
