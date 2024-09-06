from flask import Flask, request, jsonify, session
from flask_cors import CORS  # CORS 모듈 추가
from dotenv import load_dotenv
import os
from openai import OpenAI
from controller.login_controller import isValidUser

from database import get_db, init_db
from sqlalchemy import text

from config import Config
from controller.chat_controller import bp_chat

load_dotenv()
app = Flask(__name__)

# 환경변수를 사용하기 위해 Config 클래스를 사용
env_config = Config();

app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS가 아닌 환경에서 쿠키 전송 허용
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # 쿠키의 SameSite 속성 설정

# 데이터베이스 연결을 위한 세션 팩토리 생성
session_factory = init_db(env_config)

app.register_blueprint(bp_chat)

app.secret_key = os.urandom(24)  # 세션을 위한 시크릿 키 설정
CORS(app, supports_credentials=True)  # CORS 설정 적용

# OpenAI API를 사용하기 위한 인스턴스 생성
api_key = env_config.OPEN_AI_KEY
ai_model = env_config.OPENAI_MODEL_NAME
client = OpenAI(api_key=api_key)

messages = []  # 메세지들이 담기는 공간

def make_prompt(user_input):
    res = client.chat.completions.create(
        model=ai_model,
        messages=user_input
    )

    return res.choices[0].message.content  # dict: 제공

@app.route('/', methods=["POST"])
def index():
    user_id = isValidUser()
    print(user_id)

    db = next(get_db(session_factory))
    bot_response = ""
    books_data = []
    faqs_data = []

    data = request.json
    user_input = data.get('user_input').lower()  # 입력을 소문자로 변환
    print(user_input)
    # 사용자의 상태를 추적하기 위한 세션 사용
    if 'state' not in session:
        session['state'] = None

    # 사용자가 도서 검색 상태인지 확인
    if session['state'] == 'book_search':
        if "종료" in user_input:
            session['state'] = None
            bot_response = "도서 검색이 종료되었습니다."
        else:
            search_query = user_input.strip()
            print(search_query)
            query = text("""
                SELECT isbn, pub_name, pub_date, sale_stat, sale_vol, papr_pric, e_pric, sale_com, pub_review, title 
                FROM book 
                WHERE title LIKE :title
            """)
            books = db.execute(query, {"title": f"%{search_query}%"}).fetchall()

            if books:
                books_data = [
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
                    for book in books
                ]
                bot_response = "다음은 검색된 책들입니다."
            else:
                bot_response = "해당 책을 찾을 수 없습니다. 다시 검색하거나 '종료'라고 입력하세요."

    elif session['state'] == 'faq_search':
        if "종료" in user_input:
            session['state'] = None
            bot_response = "FAQ 검색이 종료되었습니다."
        else:
            search_query = user_input.strip()
            query = text("""
                SELECT title, cont, view_cnt 
                FROM faq 
                WHERE title LIKE :input OR cont LIKE :input
            """)
            faqs = db.execute(query, {"input": f"%{search_query}%"}).fetchall()

            if faqs:
                faqs_data = [
                    {
                        "title": faq.title,
                        "cont": faq.cont,
                        "view_cnt": faq.view_cnt,
                    }
                    for faq in faqs
                ]
                bot_response = "다음은 검색된 FAQ 항목들입니다."
            else:
                bot_response = "해당 FAQ 항목을 찾을 수 없습니다. 다시 검색하거나 '종료'라고 입력하세요."

    elif "책" in user_input or "isbn" in user_input or "도서" in user_input:
        session['state'] = 'book_search'
        bot_response = "도서명을 입력하세요. '종료'라고 입력하면 검색을 종료합니다."

    elif "faq" in user_input or "자주 묻는 질문" in user_input:
        session['state'] = 'faq_search'
        bot_response = "FAQ 질문을 입력하세요. '종료'라고 입력하면 검색을 종료합니다."

    else:
        # 일반 대화 처리
        conversation = [{"role": "system", "content": "You are a very kind and helpful shopping mall customer service assistant."}]
        conversation.extend([{"role": msg['role'], "content": msg['content']} for msg in messages])
        conversation.append({"role": "user", "content": user_input})

        bot_response = make_prompt(conversation)
        messages.append({'role': 'user', 'content': user_input})
        messages.append({'role': 'assistant', 'content': bot_response})
        session['state'] = None  # 대화 중에는 상태를 초기화

    return jsonify({
        'bot_response': bot_response,
        'books': books_data,
        'faqs': faqs_data
    })

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)