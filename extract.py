"""Extrair valores aninhados de uma árvore JSON."""
 
 
def json_extract(obj, key):
    """Buscar valores recursivamente do JSON aninhado."""
    arr = []
 
    def extract(obj, arr, key):
        """Pesquisar recursivamente os valores da chave na árvore JSON."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
 
    values = extract(obj, arr, key)
    return values