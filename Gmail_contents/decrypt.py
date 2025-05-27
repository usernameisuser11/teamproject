from cryptography.fernet import Fernet #암호화 라이브러리
import json
import os
def decryptCredential() :
    path = os.path.dirname(os.path.abspath(__file__))
    #credentials.json 가져와서 targetData에 저장
    with open(path+"\\Secured_credential.json","r",encoding="utf-8") as f:
        targetData = json.load(f)

    #암호화 해야하는 문자열 가져오기
    clientId = targetData["installed"]["client_id"]
    clientSecret = targetData["installed"]["client_secret"]

    #키 불러오기
    key = "s4eQbCf22ssz9lebxsvEXPWYMMXXUcTka_-dOx2SGu0="
    k = Fernet(key)

    #문자열을 바이트 형태로 저장
    clientId_byte = clientId.encode()
    clientSecret_byte = clientSecret.encode()

    #암호화
    SecuredClientId = k.decrypt(clientId_byte)
    SecuredClientSecret = k.decrypt(clientSecret_byte)

    # 딕셔너리에 암호화된 메세지 저장
    targetData["installed"]["client_id"] = SecuredClientId.decode()
    targetData["installed"]["client_secret"] = SecuredClientSecret.decode()

    #암호화된 json 파일 새로 생성
    with open(path + "\\credential.json", "w", encoding="utf-8") as f:
        json.dump(targetData, f, indent=4, ensure_ascii=False)
