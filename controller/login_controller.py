import jwt
from flask import Blueprint, request, jsonify

bp_login = Blueprint(
    name="login",
    import_name=__name__,
    url_prefix="/login"
)

# 비밀 키 (JWT 생성 시 사용한 비밀 키와 동일해야 함)
SECRET_KEY = 'SoGaYeon'

def isValidUser():
    # 요청 헤더에서 Authorization 헤더로부터 JWT 토큰 추출
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({"message": "토큰이 필요합니다!"}), 403
    
    try:
        # 'Bearer ' 부분을 제거 후 토큰만 추출
        token = token.split(" ")[1]
        
        # JWT 서명을 검증하고, 토큰을 디코딩
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # 토큰에서 유저 정보(id)를 추출 (이 경우 pswd는 토큰에 포함되지 않음이 일반적임)
        user_id = decoded.get('id')  # 토큰에서 추출한 사용자 ID
        
        # 유저가 검증되었으면 True 반환
        return user_id  # 또는 True를 반환하여 로그인 여부를 확인
    
    except jwt.ExpiredSignatureError:
        return False  # 토큰 만료 시 False 반환
    
    except jwt.InvalidTokenError:
        return False  # 유효하지 않은 토큰일 때 False 반환