import requests
import uuid
import os

def convert_hwp_to_pdf(hwp_file_path):
    # 파일을 업로드하고 응답을 얻습니다.
    with open(hwp_file_path, 'rb') as hwp_file:
        form_data = {
            'hwpj': hwp_file
        }
        response = requests.post('https://cors.bridged.cc/https://viewer.whale.naver.com/webhwpctrl/open', files=form_data)

        # 응답의 상태 코드와 내용을 출력합니다.
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")

        # JSON으로 변환을 시도합니다.
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            print("Failed to decode the response as JSON.")
            return None

        hwpj_data = response_json.get('json')

    # PDF 변환을 위한 요청 데이터를 설정합니다.
    payload = {
        'hwpj': hwpj_data,
        'id': str(uuid.uuid4()),
        'filename': os.path.basename(hwp_file_path),
        'format': '',
        'args': ''
    }

    # PDF 변환 요청을 보냅니다.
    response_pdf = requests.post('https://cors.bridged.cc/https://viewer.whale.naver.com/webhwpctrl/pdf', data=payload)
    pdf_response_json = response_pdf.json()

    # 결과 PDF 링크를 반환합니다.
    token = response_pdf.headers.get('Webhwpctrl-Auth-Token')
    pdf_url = f"https://viewer.whale.naver.com/webhwpctrl/print/{pdf_response_json['uniqueId']}/{pdf_response_json['fileName']}?token={token}"
    
    return pdf_url

# 함수 호출 예제:
hwp_file_path = "./test/12-3_고구마_표피썩음병,_수확_후_관리에_달려있어(식량원).hwp"
pdf_url = convert_hwp_to_pdf(hwp_file_path)
print(f"Converted PDF URL: {pdf_url}")
