from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI
import os
import json

from config import Config


# method name : extract_doc
# role : json 파일을 가져와서 반환한다.
# return : string
def extract_doc():
    with open('resources/api_docs.json', 'r', encoding='utf-8') as f:
        docs_json = json.load(f)
        docs = json.dumps(docs_json, indent=4, ensure_ascii=False)
    return docs

"""
CREW AI 주의 사항
- Agent 와 Task 를 2개 이상했을 때, 속도가 비약적으로 느려지는 것을 확인하였다.
- 하나의 Agent 와 Task 만을 사용하는 것을 권장한다.
"""


# method name : chat_crew
# 역할 : CREW AI 를 통한 채팅
# parameter
#  - user_input : 사용자 입력(String)
#  - chat_messages : 대화 내용(List)
# return : CREW AI 응답(String)
def chat_crew(user_input, chat_messages):
    config = Config()

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = config.OPEN_AI_KEY

    # llm model 설정
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL_NAME,
        api_key=config.OPEN_AI_KEY,
    )

    # CREW AI 설정

    # Agent back story
    api_doc_string = extract_doc()

    # API 탐색 Agent
    api_search_assistant = Agent(
        role='shopping_assistant',
        goal='고객이 어떤 상황인지 설명하면 해당 상황에 맞는 서비스를 제공하고 상황에 맞게 대화를 이어갑니다.',
        backstory="""
        당신은 고객의 상황에 맞춰서 대화를 이어나갑니다.
        당신은 고객과의 대화 내용을 고려하여 고객과 적절한 대화를 이어나갑니다.
        ===
        고객과의 대화 내용 : 
        """
        + ','.join([f"{msg['role']} : {msg['message']}" for msg in chat_messages])
        + """
        ===
        당신은 우리 도서 쇼핑몰의 모든 API 정보를 알고 있으며, 고객의 상황에 맞는 우리의 도서 쇼핑몰 API를 선택합니다.
        고객과의 대화(bot_reply), url(API 엔드포인트), method(API 메소드), available(api 요청 가능 여부) 를 반환합니다.
        available(api 요청 가능 여부)는 api 의 필수 parameter 가 없을 경우 False 를 반환합니다.
        필수 parameter 가 없을 경우 고객에게 요청해주세요. 필요한 parameter를 입력 받는 포멧을 제시합니다.
        available 이 True 일 경우에는 API가 다른 절차에 의해서 요청됩니다.
        우리의 api 문서를 참고해주세요.
        ===""" + api_doc_string,
        llm=llm
    )

    # mall_api_search_task
    mall_api_search_task = Task(
        description=user_input,
        expected_output="""
        결과는 JSON형식으로 반환해주세요.
        JSON 형식이 아닌 응답은 모두 제거해주세요.
        주석은 모두 제거합니다.
        ===
        응답 예시 :
        {
        "bot_reply": "고객과의 대화 (string)",
        "url": "API 엔드포인트 : (string)",
        "method": "API 메소드 : (string)",
        "parameters" : "필수 parameter : (dict)",
        "available": "api 요청 가능 여부 : (boolean)"
        }
        ===
        """,
        agent=api_search_assistant,
        llm=llm
    )

    assistant_crew = Crew(
        agents=[api_search_assistant],
        tasks=[mall_api_search_task],
        # debug mode
        # verbose=True
    )

    crew_result = assistant_crew.kickoff()

    text_result = str(crew_result.raw)
    # 구문 삭제
    if "my best complete final answer to the task." in text_result:
        text_result = text_result.replace("my best complete final answer to the task.", "").strip()


    try:
        json_result = json.loads(text_result)
    except:
        clean_result = text_result.strip().strip("```json").strip("```")
        return json.loads(clean_result)

    return json_result
