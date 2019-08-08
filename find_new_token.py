import requests
from requests import Session,ConnectionError,Timeout,TooManyRedirects
import json
from lastwill.swaps_common.tokentable.models import TokensCoinMarketCap


def  first_request():
    res = requests.get('https://s2.coinmarketcap.com/generated/search/quick_search.json')
    l = res.json()
    return l


def second_request(token_list):
    id = list_str = ','.join(str(e) for e in token_list)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
    parameters = {
        'id':id
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


def compare_two_json(first_json,second_json):
    a = json.loads(json_1)
    b = json.loads(json_2)
    diff = dict()
    try:
        for key['id'] in a.keys():
            if key['token_cmc_id'] not in b:
                diff['id'] = key['id']
    except:
        pass
        return diff


def find_by_parameters():
    l = first_request()
    from_db =TokensCoinMarketCap.objects.all().values_list('id', flat=True)
    #values cmc
    if len(l) != quantity.count():
        diff =compare_two_json(l)
        new_ids = dict()
        for key in  diff.keys()
            info_for_save = second_request(id)
            new_ids = info_for_save


def save_into_base(dict_for_save):
    for key in dict_for_save:
            obj = TokensCoinMarketCap(token_cmc_id = key['id'], token_name = key['name'],
                                    token_short_name = key['symbol'], image_link = key['logo'],
                                    token_rank = key['rank'],token_platform = key['slug'],token_address = key['token_address'])
            """
            platform_data = dict_json[item]['platform']
            if platform_data is not None:
                token.token_platform = platform_data['slug']
                token.token_address = platform_data['token_address']
            else:
                token.token_platform = None
                token.token_address = '0x0000000000000000000000000000000000000000'
            """

            obj.save()


def find_new_tokens():
    values_for_save = find_by_parameters()
    save_into_base(values_for_save)



if __name__ =="__main__":
    find_new_tokens()
