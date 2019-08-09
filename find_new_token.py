import requests
from requests import Session,ConnectionError,Timeout,TooManyRedirects
import json
from lastwill.swaps_common.tokentable.models import TokensCoinMarketCap


def  first_request():
    res = requests.get('https://s2.coinmarketcap.com/generated/search/quick_search.json')
    l = res.json()
    id_rank = {}
    for i in range(len(l)):
        id_rank[(l[i]['id'])] =l[i]['rank']
    return id_rank


def second_request(token_list):
    key = [key[0] for key in token_list.items()]
    id = ','.join(str(k) for k in key)
    print(id)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
    parameters = {
        'id': id
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'f66f6d8d-742d-4ba7-af33-e61a55c7c135',
    }
    #rebuild to list values
    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        print(response.text)
        data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return data

def find_by_parameters():
    db =TokensCoinMarketCap.objects.all().values_list('token_cmc_id', flat=True)
      #convert to list
    ids = first_request()
    id_from_market = [i for i in ids.keys()]
    id_from_db = [id for id in db ]
    if len(list(id_from_market)) != len(id_from_db):
        result = list(set(id_from_market)-set(id_from_db))
        id_rank ={}
        for key,value in ids.items():
                if key in  result:
                     id_rank[key] = value
    print((id_rank))
    info_for_save = second_request(id_rank)
    for key,value in info_for_save['data'].items():
        obj = TokensCoinMarketCap(token_cmc_id =value ['id'], token_name = value['name'],
                                        token_short_name = value['symbol'], image_link =value['logo'],
                                        token_rank = 1 ,token_platform =value['slug'],token_address = value['token_address']
                                        )
def find_new_tokens():
    values_for_save = find_by_parameters()
