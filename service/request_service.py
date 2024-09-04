from sqlalchemy import text

from config import Config
from database import get_db, init_db
from dto.chat_response_dto import ChatResponseDto

"""
role : prompt 결과를 실행시켜주는 메서드
method name : prompt_executor
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


def prompt_executor(crew_response) -> ChatResponseDto:
    url = crew_response['url']
    method = crew_response['method']

    # available 이 False 일 경우
    if not crew_response['available']:
        chat_response: ChatResponseDto = ChatResponseDto(
            bot_reply=crew_response['bot_reply'],
            reply_content=[]
        )
        return chat_response

    # crew_response 의 결과에 따른 분기 처리
    if '/book/list' in url:
        # 책 검색
        chat_response: ChatResponseDto = _search_book(crew_response)
        return chat_response

    if '/faq/list' in url:
        # FAQ 검색
        chat_response: ChatResponseDto = _search_faq(crew_response)
        return chat_response

    # 기본적인 채팅 응답
    chat_response: ChatResponseDto = ChatResponseDto(
        bot_reply=crew_response['bot_reply'],
        reply_content=[]
    )
    return chat_response


"""
role : /book/list 요청에 대한 응답을 반환하는 역할
parameter : crew_response:dict
return : ChatResponseDto
    bot_reply : str
    reply_content : list<book>
        book : dict
            title : str
            isbn : str
            pub_name : str
            pub_date : str
            sale_stat : str
            sale_vol : str
            papr_pric : int
            e_pric : int
            sale_com : str
            pub_review : str
"""


def _search_book(crew_response):
    config = Config()
    session_factory = init_db(config)
    db = next(get_db(session_factory))

    parameters = crew_response['parameters']
    query_title = parameters['title'].strip()
    query = text("""
                    SELECT isbn, pub_name, pub_date, sale_stat, sale_vol, papr_pric, e_pric, sale_com, pub_review, title 
                    FROM book 
                    WHERE title LIKE :title
                """)
    book_list = db.execute(query, {"title": f"%{query_title}%"}).fetchall()

    reply_content = [
        {
            "title": book.title,
            "isbn": book.isbn,
            "pub_name": book.pub_name,
            "pub_date": book.pub_date,
            "sale_stat": book.sale_stat,
            "sale_vol": book.sale_vol,
            "papr_pric": book.papr_pric,
            "e_pric": book.e_pric,
            "sale_com": book.sale_com,
            "pub_review": book.pub_review,
        }
        for book in book_list
    ]

    chat_dto = ChatResponseDto(
        bot_reply=crew_response['bot_reply'],
        reply_content=reply_content
    )

    return chat_dto

"""
role : /faq/list 요청에 대한 응답을 반환하는 역할
parameter : crew_response:dict
return : ChatResponseDto
    bot_reply : str
    reply_content : list<faq>
        faq : dict
            title : str
            content : str
            view_cnt : int
"""
def _search_faq(crew_response):
    config = Config()
    session_factory = init_db(config)
    db = next(get_db(session_factory))

    parameters = crew_response['parameters']
    user_input = parameters['title_or_content'].strip()
    query = text("""
                    SELECT title, cont, view_cnt 
                    FROM faq 
                    WHERE title LIKE :input OR cont LIKE :input
                """)
    faq_list = db.execute(query, {"input": f"%{user_input}%"}).fetchall()

    reply_content = [
        {
            "title": faq.title,
            "content": faq.cont,
            "view_cnt": faq.view_cnt,
        }
        for faq in faq_list
    ]

    chat_dto = ChatResponseDto(
        bot_reply=crew_response['bot_reply'],
        reply_content=reply_content
    )

    return chat_dto