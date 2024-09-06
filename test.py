import jwt
import datetime
import base64

# 비밀키 및 알고리즘 설정
SECRET_KEY = "SoGaYeon"
SIGNATURE_ALGORITHM = 'HS256'

# JWT 토큰 생성 함수
def generate_token(user_id):
    payload = {
        'iss': 'hongildong',  # 발행자 (Issuer)
        'iat': datetime.datetime.utcnow(),  # 발행 시간 (Issued At)
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # 만료 시간 (1시간 뒤)
        'userID': user_id  # 사용자 정보 (예: userID)
    }

    # 토큰 생성
    token = jwt.encode(payload, SECRET_KEY, algorithm=SIGNATURE_ALGORITHM)
    return token

# JWT 토큰 검증 함수
def validate_token(token):
    try:
        # 토큰 디코딩 및 검증
        decoded = jwt.decode(token)
        return decoded
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

print(SECRET_KEY)

# 토큰 생성
user_id = "asdfg"
token = generate_token(user_id)
print("Generated token:", token)

# 토큰 검증
decoded_token = validate_token("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJob25naWxkb25nIiwiaWF0IjoxNzI1NjE2MjA3LCJleHAiOjE3MjU2MTk4MDcsInVzZXJJRCI6InRlc3RVc2VyIn0.vNhES-P0mAnmPusrm8msMgVryDb-C0YrnHQILvrqfAg")
print("Decoded token:", decoded_token)