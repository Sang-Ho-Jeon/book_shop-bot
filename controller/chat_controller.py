from flask import Blueprint, request, jsonify

from dto.chat_response_dto import ChatResponseDto
from service import crew_service, request_service

bp_chat = Blueprint(
    name="chat",
    import_name=__name__,
    url_prefix="/chat"
)

chat_messages = []



"""
api : /chat/crew
method: GET
description: CREW AI 를 통한 채팅
work
    1. service.chat_service.chat_crew() 호출
    2. 반환값 리턴
"""


@bp_chat.route("", methods=["POST"])
def chat_crew_controller():
    data = request.json
    user_input = data.get('user_input')

    # CREW AI 를 통한 채팅
    crew_result = crew_service.chat_crew(user_input, chat_messages)

    # TODO : crew_result[available] 가 True 일 때만 실행할 수 있도록 변경
    chat_dto: ChatResponseDto = request_service.prompt_executor(crew_result)

    # 결과 종합
    total_bot_reply = chat_dto

    # TODO : chat_messages 를 DB 에 연결하여 사용할 수 있도록 변경
    chat_messages.append({
        'role': 'user',
        'message': user_input,
    })
    chat_messages.append({
        'role': 'assistant',
        'message': total_bot_reply
    })

    return jsonify({
        'bot_response': chat_dto.bot_reply,
        'content' : chat_dto.reply_content,
        'url': crew_result['url']
    })
