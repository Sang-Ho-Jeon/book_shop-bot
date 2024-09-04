from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

def init_db(env_config):
    # 환경 변수 셋팅
    user_id = env_config.DATABASE_USERID
    password = env_config.DATABASE_PASSWORD
    host = env_config.DATABASE_HOST
    schema = env_config.DATABASE_SCHEMA

    # MySQL 데이터 베이스 설정
    database_url = f"mysql+pymysql://{user_id}:{password}@{host}/{schema}"

    # MySQL 데이터 베이스 엔진 생성
    engine = create_engine(database_url)

    # 모델에서 정의된 테이블 생성
    Base.metadata.create_all(bind=engine)

    # 세션 생성기 설정 및 반환
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db(session_factory):
    db = session_factory()
    try:
        yield db
    finally:
        db.close()