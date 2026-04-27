from profanityfilter import ProfanityFilter

pf = ProfanityFilter()

def contains_profanity(text: str) -> bool:
    # Retorna True si el texto contiene alguna palabra ofensiva
    return pf.is_profane(text)
