import requests
from requests import Session,ConnectionError,Timeout,TooManyRedirects
import json
from lastwill.swaps_common.tokentable.models import TokensCoinMarketCap


def  first_request():
    res = requests.get('https://s2.coinmarketcap.com/generated/search/quick_search.json')
    l = res.json()
    id_rank = dict()
    for i in range(len(l)):
        id_rank['{}'.format((l[i]['id']))] = l[i]['rank']

    return id_rank


def second_request(token_list):
    id = list_str = ','.join(str(key) for key in token_list.items())
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
        data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return data

def find_by_parameters():
    l = first_request()
    print(l)
    db =TokensCoinMarketCap.objects.all().values_list('token_cmc_id', flat=True)
      #convert to list
    id_from_market = [key for key in l.keys()]
    id_from_db = [id for id in db ]
    print('*'*10)
     if len(l) != len(id_from_db):
        result = set(l) - set(id_from_db)
        new_id = filter(None,result)
        print("&"*50)
        print(new_id)
        print("%"*50)
        print(l)
        info = dict()
        for id in new_id:
            for key,value in l.items():
                if  id == key:
                    info[key] = value
        print(info)
        info_for_save = second_request(info)
        return info_for_save


def save_into_base(dict_for_save,rank):
    for key,value in dict_for_save['data'].items():
            obj = TokensCoinMarketCap(token_cmc_id =value ['id'], token_name = value['name'],
                                    token_short_name = value['symbol'], image_link =value['logo'],
                                    token_rank = rank[key]['rank'],token_platform =value['slug'],token_address = value['token_address'])
            platform_data = value['platform']
            if platform_data is not None:
                token.token_platform = platform_data['slug']
                token.token_address = platform_data['token_address']
            else:
                token.token_platform = None
                token.token_address = '0x0000000000000000000000000000000000000000'

            obj.save()

def find_new_tokens():
    values_for_save = find_by_parameters()
    save_into_base(values_for_save)
