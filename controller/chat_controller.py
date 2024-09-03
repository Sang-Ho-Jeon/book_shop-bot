from flask import Blueprint, request, jsonify

from service import crew_service, request_service

bp_chat = Blueprint(
    name="chat",
    import_name=__name__,
    url_prefix="/chat"
)

chat_messages = []


@bp_chat.route("", methods=["GET"])
def chat():
    return "Chat Controller"


"""
api : /chat/crew
method: GET
description: CREW AI 를 통한 채팅
work
    1. service.chat_service.chat_crew() 호출
    2. 반환값 리턴
"""


@bp_chat.route("/crew", methods=["POST"])
def chatCrew():
    print(chat_messages)
    data = request.json
    user_input = data.get('user_input')

    # CREW AI 를 통한 채팅
    crew_result = crew_service.chat_crew(user_input, chat_messages)

    # spring 서버에 api 요청
    spring_result = request_service.search_api(crew_result)

    # 결과 종합
    bot_response = crew_result['bot_response']

    # TODO : chat_messages 를 DB 에 연결하여 사용할 수 있도록 변경
    chat_messages.append({
        'role': 'user',
        'message': user_input,
    })
    chat_messages.append({
        'role': 'bot',
        'message': bot_response
    })

    return jsonify({
        'bot_response': str(crew_result),
    })
