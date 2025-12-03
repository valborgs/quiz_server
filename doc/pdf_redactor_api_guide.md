# PDF Redactor API 사용 가이드

이 문서는 `pdfredactor` 앱에서 제공하는 PDF 마스킹(Redaction) API의 사용 방법을 설명합니다.

## 개요

이 API는 클라이언트로부터 PDF 파일과 마스킹할 영역의 좌표 정보를 받아, 해당 영역의 데이터를 영구적으로 삭제(Sanitize)하고 검은색으로 칠한 뒤 처리된 PDF 파일을 반환합니다.

## 엔드포인트 정보

- **URL**: `/api/pdf/redact/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

## 요청 파라미터 (Request Body)

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :--- | :--- |
| `file` | File | 필수 | 마스킹을 적용할 원본 PDF 파일입니다. |
| `redactions` | String (JSON) | 필수 | 마스킹할 영역들의 좌표 정보를 담은 JSON 문자열입니다. |

### `redactions` JSON 구조

`redactions` 파라미터는 다음과 같은 객체들의 배열(Array) 형태여야 합니다.

```json
[
  {
    "pageIndex": 0,       // (Integer) 페이지 번호 (0부터 시작)
    "x": 100.0,           // (Float) 영역의 왼쪽 상단 x 좌표
    "y": 200.0,           // (Float) 영역의 왼쪽 상단 y 좌표
    "width": 50.0,        // (Float) 영역의 너비
    "height": 20.0,       // (Float) 영역의 높이
    "color": -16777216    // (Integer, Optional) 마스킹 색상 (현재는 검은색으로 고정됨)
  }
]
```

- **좌표계**: PDF의 기본 좌표계(Points)를 따르며, 좌측 상단이 (0, 0)입니다. 안드로이드 Canvas 좌표와 호환됩니다.

## 응답 (Response)

### 성공 (200 OK)

- **Content-Type**: `application/pdf`
- **Content-Disposition**: `attachment; filename="redacted_result.pdf"`
- **Body**: 처리된(마스킹 적용된) PDF 파일의 바이너리 데이터.

### 실패 (400 Bad Request)

요청 파라미터가 누락되었거나 JSON 형식이 올바르지 않은 경우 반환됩니다.

```json
{
  "error": "Both 'file' and 'redactions' are required."
}
```
또는
```json
{
  "error": "Invalid JSON format for 'redactions'."
}
```

### 실패 (500 Internal Server Error)

서버 내부 오류 발생 시 반환됩니다.

```json
{
  "error": "Error message details..."
}
```

## 예시 (Python Requests)

```python
import requests
import json

url = "http://localhost:8000/api/pdf/redact/"
file_path = "example.pdf"

# 마스킹할 영역 정보
redactions = [
    {
        "pageIndex": 0,
        "x": 50,
        "y": 50,
        "width": 100,
        "height": 50
    }
]

with open(file_path, 'rb') as f:
    files = {'file': f}
    data = {'redactions': json.dumps(redactions)}
    
    response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    with open("redacted_output.pdf", 'wb') as f:
        f.write(response.content)
    print("마스킹 완료: redacted_output.pdf 저장됨")
else:
    print(f"오류 발생: {response.text}")
```
