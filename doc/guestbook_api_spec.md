# 방명록 API 명세서

방명록 조회, 작성, 삭제를 위한 API 명세서입니다.

## Base URL
`http://{server_address}/api`

---

## 1. 방명록 목록 조회

방명록 목록을 페이지네이션하여 조회합니다.

**Endpoint:** `GET /guestbook/`

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | 페이지 번호 (기본값: 1) |
| `page_size` | integer | No | 페이지당 항목 수 (기본값: 5, 최대: 20) |

### Response (200 OK)

```json
{
    "count": 25,
    "next": "http://{server_address}/api/guestbook/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "행복한 고양이42",
            "content": "응원합니다!",
            "created_at": "2025-12-16T21:30:00Z"
        }
    ]
}
```

---

## 2. 방명록 작성

새로운 방명록을 작성합니다.

**Endpoint:** `POST /guestbook/`

### Request Body

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | No | 최대 20자 | 작성자 이름. 미입력 시 서버에서 "형용사 + 동물 + 숫자" 조합의 익명 이름 자동 생성 (예: "행복한 고양이42") |
| `password` | string | Yes | 최대 20자 | 삭제 시 본인 확인을 위한 비밀번호 (저장 시 암호화됨) |
| `content` | string | Yes | 최대 200자 | 방명록 내용. 최대 4줄까지만 입력 가능 |

**Request 예시:**
```json
{
    "name": "방문자",
    "password": "mypassword123",
    "content": "좋은 사이트네요!\n자주 오겠습니다."
}
```

### Response (201 Created)

성공적으로 생성된 방명록 정보를 반환합니다. (비밀번호 제외)

```json
{
    "id": 3,
    "name": "방문자",
    "content": "좋은 사이트네요!\n자주 오겠습니다.",
    "created_at": "2025-12-16T22:00:00Z"
}
```

### Error Responses

**400 Bad Request (유효성 검사 실패)**

```json
{
    "content": ["최대 4줄까지 입력 가능합니다."],
    "password": ["이 필드는 필수 항목입니다."]
}
```

---

## 3. 방명록 삭제

작성 시 입력한 비밀번호를 확인하여 방명록을 삭제합니다.

**Endpoint:** `DELETE /guestbook/{id}/`

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | 삭제할 방명록 ID |

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `password` | string | Yes | 작성 시 등록한 비밀번호 |

**Request 예시:**
```json
{
    "password": "mypassword123"
}
```

### Response (204 No Content)

성공 시 응답 본문 없이 204 코드를 반환합니다.

### Error Responses

**400 Bad Request - 비밀번호 불일치**

```json
{
    "error": "password_mismatch",
    "message": "비밀번호가 일치하지 않습니다."
}
```

**404 Not Found - 해당 글 없음**

```json
{
    "error": "not_found",
    "message": "해당 글을 찾을 수 없습니다."
}
```

---

## 부록: CORS 설정 가이드 (Django)

GitHub Pages와 같이 다른 도메인에서 API를 호출하려면 Django 서버에 CORS(Cross-Origin Resource Sharing) 설정이 필요합니다.

### 1. 패키지 설치

`django-cors-headers` 패키지를 설치합니다.

```bash
pip install django-cors-headers
```

### 2. settings.py 수정

`settings.py` 파일에 다음 설정을 추가/수정합니다.

**INSTALLED_APPS 추가:**
```python
INSTALLED_APPS = [
    # ... 기존 앱들 ...
    "corsheaders",  # 반드시 최상단이나 공통 앱(django.contrib...) 다음에 위치시키는 것이 좋습니다.
    # ...
]
```

**MIDDLEWARE 추가:**
중요: `CorsMiddleware`는 가능한 한 상단에, 특히 `CommonMiddleware`보다는 **반드시 위에** 위치해야 합니다.

```python
MIDDLEWARE = [
    # ...
    "corsheaders.middleware.CorsMiddleware",  # 최상단 권장
    "django.middleware.common.CommonMiddleware",
    # ...
]
```

**CORS 허용 도메인 설정:**
`CORS_ALLOWED_ORIGINS` 리스트에 배포된 프론트엔드 도메인을 추가합니다.

```python
CORS_ALLOWED_ORIGINS = [
    "https://ums1212.github.io",
    # 로컬 테스트용 (필요 시)
    # "http://localhost:8000",
    # "http://127.0.0.1:8000",
]
```

### 3. 변경사항 확인

서버를 재시작하면 해당 도메인에서의 API 요청이 허용됩니다.
