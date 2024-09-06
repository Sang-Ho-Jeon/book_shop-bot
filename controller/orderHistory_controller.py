from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Spring 서버 URL 설정 (JWT 검증 요청을 보낼 주소)
SPRING_SERVER_URL = "http://localhost:8080/validateToken"

@app.route('/order-history', methods=['POST'])
def order_history():
    # 브라우저에서 JWT 토큰을 Authorization 헤더로 전달
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Authorization 헤더에 JWT 토큰이 필요합니다."}), 400

    # Spring 서버에 JWT 검증 요청 보내기
    spring_response = requests.post(SPRING_SERVER_URL, headers={"Authorization": token})

    # 검증 결과 확인
    if spring_response.status_code == 200 and spring_response.json().get("valid") == True:
        # Spring 서버에서 검증이 성공하면 사용자 주문 내역을 응답
        user_id = spring_response.json().get("userID")
        
        # DB에서 사용자 주문 내역을 조회하는 코드
        # 예: order_history = db.query("SELECT * FROM orders WHERE user_id = ?", (user_id,))

        order_history = [
            {"order_id": 1, "product": "Laptop", "price": 1200},
            {"order_id": 2, "product": "Mouse", "price": 50}
        ]

        return jsonify({
            "message": "주문 내역 조회 성공",
            "orders": order_history
        })
    else:
        # JWT 검증이 실패하면 로그인 요청 메시지를 응답
        return jsonify({"message": "로그인 후 질문해주세요."}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)