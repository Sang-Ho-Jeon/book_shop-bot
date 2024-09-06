from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
from flask import Blueprint, request, jsonify
import datetime

# JWT Configuration
SECRET_KEY = 'SoGaYeon'
SIGNATURE_ALGORITHM = 'HS256'

def isValidUser():
    # Extract JWT token from the Authorization header
    token = request.headers.get('Authorization')
    print("Received token:", token)
    
    if not token:
        return {"message": "Token is required!"}, 403

    # Check if the token format is correct
    if not token.startswith("Bearer "):
        return {"message": "Incorrect token format!"}, 400

    try:
        # Remove 'Bearer ' prefix and strip any whitespace
        token = token.split(" ")[1].strip()
        
        # Decode the JWT token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[SIGNATURE_ALGORITHM])
        print("Decoded token:", decoded)

        # Extract user ID from token (assuming 'sub' is used as the subject identifier)
        user_id = decoded.get('sub')
        print("User ID from token:", user_id)

        # If user is verified, return user ID
        return user_id

    except ExpiredSignatureError:
        print("Token has expired")
        return {"message": "Token has expired"}, 401

    except JWTClaimsError as e:
        print("Invalid claims in token:", str(e))
        return {"message": "Invalid claims: " + str(e)}, 403

    except JWTError as e:
        print("Invalid token:", str(e))
        return {"message": "Invalid token: " + str(e)}, 403

    except Exception as e:
        print("Unexpected error:", str(e))
        return {"message": "Unexpected error: " + str(e)}, 500