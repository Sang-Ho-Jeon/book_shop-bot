import requests


"""
role : 요청할 url를 받아서 결과를 반환하는 역할
method name : search_api
parameter : crew_response:dict
    bot_response : str
    url : str
    method : str
return : dict
    bot_response : str
    url : str
    method : str
    response : str
    status_code : int
"""

def search_api(crew_response):
    url = crew_response['url']
    method = crew_response['method']

    # crew_response 의 결과에 따른 분기 처리
    if url == '/book/list':
        print('/book/list')




    return {
        'bot_response': crew_response['bot_response'],
        'url': url,
        'method': method,
        # 'response': response.text,
        # 'status_code': response.status_code
    }