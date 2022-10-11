""" @Preparar tweets coletados para instalação no CQPweb

Este script prepara tweets coletados com get_tweets_by_userid da seguinte forma
    - elimina retweets
    - elimina boilerplates (ex: "Acabei de ver", "Clique para ver também")
    - adiciona etiqueta xml com id para cada texto
    - salva os metadados em formato tabular
    - tokeniza e anota o texo para lema e clase gramatical
    - salva os textos em xml e os metadados em tsv

"""
 
 
# importar bibliotecas
from bs4 import BeautifulSoup
import re
import pathlib
import spacy


# carregar modelo 
nlp = spacy.load('pt_core_news_lg')
 
# definir o diretório onde os arquivos estão
workingDir = pathlib.Path("../folha")

# criar uma lista e adicionar o nome dos arquivos a ela
file_list = []
for f in workingDir.iterdir():
    file_list.append(f)
 
 
# criar strings vazios para adicionar o texto etiquetado e os metadados
tagged_text = ""
meta_text = ""
count = 1
 
# iterar por todos os arquivos na lista
for val in file_list:
    # read the file
    with open(val, 'r') as f:
        data = f.read()
    
    # parse the data
    bs_data = BeautifulSoup(data, features="xml")
 
    # encontrar e remover os retweets
    retweets = bs_data.find_all("text", string=re.compile(r'^RT \@'))
    for r in range(len(retweets)):
        retweets[r].decompose()
 
    # encontrar todos os text restantes
    bs_texts = bs_data.find_all('text')
 
    # para todos os text no arquivo
    for t in range(len(bs_texts)):
        # remover ruídos
        bs_texts[t].string = re.sub(r'^Acabei de ver ', '', bs_texts[t].string)
        bs_texts[t].string = re.sub('- Clique para ver também ☛', '', bs_texts[t].string)
        bs_texts[t].string = re.sub('NOTICIAS AO MINUTO:', '', bs_texts[t].string)
        
        # obter metadados
        pt_var = bs_texts[t]['pt']
        grupo = bs_texts[t]['group']
        subgrupo = bs_texts[t]['subgroup']
        author = bs_texts[t]['author']
        twid = bs_texts[t]['tweetid']
        dia = bs_texts[t]['date']
        year = bs_texts[t]['year']

        # adicionar da etiqueta raíz a cada texto (com metadados)
        tagged_text += '<text id="tweet' + str(count) + '" pt="' + pt_var + '" group="' + grupo + '" subgroup="' + subgrupo + '" author="' + author + '" tweetid="' + twid + '" date="' + dia + '" year="' + year + '">\n'
        
        # adicionar metadados em formato tabular
        meta_text += 'tweet' + str(count) + '\t' + pt_var + '\t' + grupo + '\t' + subgrupo + '\t' + author + '\t' + twid + '\t"' + dia + '"\t' + year + '\n'

        # aplicar modelo ao text string
        nlp_text = nlp(str(bs_texts[t].string))
        # adicionar em formato VRT um token por linha seguido de seus respectivos lema e classe gramatical
        for token in nlp_text:
            tagged_text += str(token.text) + "\t" + str(token.lemma_) + "\t" + str(token.tag_) + "\n"
        tagged_text += '</text>\n'
        count += 1
    
    # remover espaços em branco
    tagged_text1 = re.sub(r'.*SPACE.*\n', '', tagged_text)
    # encapsular links de site em uma etiqueta XML
    tagged_text2 = re.sub(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])).*", r'<link val="\1"/>', tagged_text1)
 
# salvar o texto em xml
with open("cplp_tuites.xml", 'w') as f:
    f.write(tagged_text2)
 
# e os metadados em tsv
with open("meta_tuites.tsv", 'w') as f:
    f.write(meta_text)
 
 