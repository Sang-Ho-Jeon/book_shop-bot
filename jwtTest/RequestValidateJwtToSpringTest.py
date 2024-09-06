from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Spring 서버 URL 설정 (JWT 검증 요청을 보낼 주소)
SPRING_SERVER_URL = "http://localhost:8080/ch4/validateToken"

@app.route('/test-jwt-validation', methods=['POST'])
def test_jwt_validation():
    print("옴")
    # 브라우저에서 JWT 토큰을 Authorization 헤더로 전달
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Authorization 헤더에 JWT 토큰이 필요합니다."}), 400

    # Spring 서버에 JWT 검증 요청 보내기
    spring_response = requests.post(SPRING_SERVER_URL, headers={"Authorization": token})
    print(spring_response)
    # 검증 결과 확인
    if spring_response.status_code == 200 and spring_response.json().get("valid") == True:
        # 검증 성공 시 메시지 출력
        return jsonify({"message": "JWT 검증에 성공했습니다."}), 200
    else:
        # 검증 실패 시 메시지 출력
        return jsonify({"message": "JWT 검증에 실패했습니다."}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)