""" @Coleta de tweets por id de usuário

Este script utiliza o API do twitter
para coletar tweets por usuários
e converter o json obtido em XML
preservando o id e a data de publicação do tweet

Funções neste arquivo
    * create_url - criar o URL com base no id do usuário
    * get_params - estabelece os parametros desejados
    * bearer_oauth - método para autentificação por bearer token 
    * connect_to_endpoint - request

(este código é uma adaptação de códigos gentilmente compartilhados por Tiago Januário)
"""

import requests
from extract import json_extract
import os
import xml.etree.ElementTree as ET
import datetime
 
# para configurar as variáveis, execute a seguinte linha
# export 'BEARER_TOKEN'='<o_seu_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")
 
def create_url():
    """ Creates a API URL for requests """
    # TODO add user_id as argument
    user_id = 347348912
    return "https://api.twitter.com/2/users/{}/tweets".format(user_id)
 
def get_params():
    # Os campos dos tweets são ajustáveis
    # As opções são:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    # para este corpus utilizamos apenas data de criação
    return {"tweet.fields": "created_at"}
 
def bearer_oauth(r):
    """
    Método para autentificação por bearer token 
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r
 
def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()
 
 
  
def main():  
    xml = ET.Element('xml')
    token = ''
    stop = False
    params = get_params()
 
    while True:  
        # Create query URL                                   
        json_response = ''
        if token == '':
            url = create_url()
        else:
            url = create_url() + "?pagination_token=" + token
        try:
            json_response = connect_to_endpoint(url, params)
        except Exception as e:
            print(e.args)
            print("Oh no!!!")
 
        id = json_extract(json_response, 'id')
        created_at = json_extract(json_response, 'created_at')
        text = json_extract(json_response, 'text')
 
        tweetsList = list(text)
        tweetsList = [i.replace('\n',' ') for i in tweetsList]
        tweetsList = [i.replace('\r',' ') for i in tweetsList]
    
 
        for u, d, t in zip(id, created_at, tweetsList):  
            date = datetime.datetime.strptime(d,"%Y-%m-%dT%H:%M:%S.%fZ")
 
            tweet = ET.SubElement(xml, 'text')
            # TODO CHANGE THIS, GET FROM ARGUMENT
            tweet.set('pt', 'br')
            tweet.set('group', 'other')
            tweet.set('subgroup', 'twitter')
            # TODO CHANGE THIS (ADD FUNCTION TO GET NAME AND CONVERT TO ID)
            tweet.set('author', 'folha') 
            tweet.set('tweetid', u)
            tweet.set('date', str(d))
            tweet.set('year', str(d)[:4])
            tweet.text = str(t)
 
            # print
            print(len(xml.findall('text')),"tweets for user since ", date)
 
        try:
            token = json_extract(json_response, 'next_token')[0]                
        except:       
            print("finished")         
            stop = True
 
        if stop:
            break     
        # break       
 
        tree = ET.ElementTree(xml)
        ET.indent(tree, space="\t", level=0)
        # TODO use username as name of the file
        tree.write("out_twe_br_folha.xml")
 
 
if __name__ == '__main__':
    main()
 
 