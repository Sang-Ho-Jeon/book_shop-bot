from xml.etree.ElementTree import indent

from crewai import Crew, Agent, Task
from crewai_tools import JSONSearchTool
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

    # agent 설정
    # shopping_assistant = Agent(
    #     role='도서 쇼핑몰 API 활용 어시스턴트',
    #     goal='고객이 어떤 상황인지 설명을 하면 해당 상황에 맞는 우리 도서 쇼핑몰의 API를 알려줍니다.',
    #     backstory='당신은 우리 도서 쇼핑몰에서 제공하는 API 를 사용하여 고객에게 도움을 주는 어시스턴트입니다.',
    #     tools=[txt_search_tool],
    #     llm=llm
    # )

    # Agent back story
    api_doc_string = extract_doc()

    # # 대화형 Agent
    # talk_assistant = Agent(
    #     role='대화형 어시스턴트',
    #     goal='고객과 대화를 이어나가며 고객의 쇼핑몰 이용을 보조합니다. API 에 대한 정보는 필요하지 않습니다. 상황에 맞는 API 가 없다면 대화를 그대로 이어갑니다.',
    #     backstory='당신은 고객과 대화를 이어나가며 우리의 도서 쇼핑몰에 대한 정보를 전달하는 어시스턴트입니다. 우리의 api 문서입니다. 참고해주세요. ===' + api_doc_string,
    #     llm=llm
    # )

    # API 탐색 Agent
    api_search_assistant = Agent(
        role='shopping_assistant',
        goal='고객이 어떤 상황인지 설명하면 해당 상황에 맞는 서비스를 제공하고 상황에 맞게 대화를 이어갑니다.',
        backstory="""
        당신은 고객의 상황에 맞춰서 대화를 이어나갑니다.
        당신과 고객의 대화내용 입니다.
        ===
        대화 내용 : 
        """
        + ','.join([f"{msg['role']} : {msg['message']}" for msg in chat_messages])
        + """
        ===
        당신은 우리 도서 쇼핑몰의 모든 API 정보를 알고 있으며, 고객의 상황에 맞는 우리의 도서 쇼핑몰 API를 선택합니다.
        고객과의 대화(bot_response), url(API 엔드포인트), method(API 메소드), available(api 요청 가능 여부) 를 반환합니다.
        available(api 요청 가능 여부)는 api 의 필수 parameter 가 없을 경우 False 를 반환합니다.
        필수 parameter 가 없을 경우 고객에게 요청해주세요.
        우리의 api 문서를 참고해주세요.
        ===""" + api_doc_string,
        llm=llm
    )
        # API는 요청하기 위한 어떠한 정보(필수 정보 포함)도 요구하지 않습니다.

    # # shopping_assist_task
    # shopping_assist_task = Task(
    #     description=user_input,
    #     expected_output='고객과 대화하면서 고객의 상황에 맞게 말해줘 (API 는 필요없음)',
    #     agent=talk_assistant,
    #     llm=llm
    # )

    # mall_api_search_task
    mall_api_search_task = Task(
        description=user_input,
        expected_output="""
        결과는 JSON형식으로 반환해주세요. (JSON 형식이 아닌 다른 응답은 모두 제거해주세요.)
        주석은 모두 제거합니다.
        ===
        응답 예시 :
        {
        "bot_response": "고객과의 대화 (string)",
        "url": "API 엔드포인트 : (string)",
        "method": "API 메소드 : (string)"
        "available": "api 요청 가능 여부 : (boolean)"
        }
        ===
        """,
        agent=api_search_assistant,
        llm=llm
    )

    # assistant_crew = Crew(
    #     agents=[talk_assistant, api_search_assistant],
    #     tasks=[shopping_assist_task, mall_api_search_task],
    #     verbose=True
    # )

    assistant_crew = Crew(
        agents=[api_search_assistant],
        tasks=[mall_api_search_task],
        verbose=True
    )

    crew_result = assistant_crew.kickoff()

    text_result = str(crew_result.raw)
    try:
        json_result = json.loads(text_result)
    except:
        clean_result = text_result.strip().strip("```json").strip("```")
        return json.loads(clean_result)


    print(1, json_result['bot_response'])
    return json_result
