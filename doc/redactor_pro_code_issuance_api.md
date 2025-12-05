# Redactor Pro Code Issuance API 명세서

`redactor_pro_code_issuance` 앱에서 제공하는 리딤코드 발급 및 검증 API에 대한 명세입니다.

## Base URL
`/api/redeem/`

---

## 1. 리딤코드 발급 (Issue Code)

이메일 주소를 입력받아 8자리 리딤코드를 발급합니다.
항상 새로운 리딤코드를 생성하여 반환합니다. (중복 이메일 허용)

### 요청 (Request)

- **URL**: `/api/redeem/issue/`
- **Method**: `POST`
- **Content-Type**: `application/json`

**Body Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `email` | string | Yes | 사용자 이메일 주소 |

**Example:**
```json
{
  "email": "user@example.com"
}
```

### 응답 (Response)

**Success (201 Created)**
```json
{
  "email": "user@example.com",
  "code": "AB12CD34",
  "is_new": true,
  "message": "새 리딤코드를 발급했습니다."
}
```

**Error (400 Bad Request)**
```json
{
  "email": [
    "유효한 이메일 주소를 입력하십시오."
  ]
}
```

---

## 2. 리딤코드 검증 및 사용 (Validate Code)

이메일과 리딤코드를 입력받아 유효성을 검증하고 사용 처리(`is_used=True`)합니다.
- 코드가 유효하고 사용되지 않은 경우: 사용 처리 후 성공 응답을 반환합니다.
- 이미 사용된 코드인 경우: 실패 응답을 반환합니다.
- 이메일과 코드가 일치하지 않거나 없는 경우: 실패 응답을 반환합니다.

### 요청 (Request)

- **URL**: `/api/redeem/validate/`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Headers**:
    - `X-Redeem-Api-Key`: `16자리 랜덤 문자열` (필수)

**Body Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `email` | string | Yes | 사용자 이메일 주소 |
| `code` | string | Yes | 8자리 리딤코드 |

**Example:**
```json
{
  "email": "user@example.com",
  "code": "AB12CD34"
}
```

### 응답 (Response)

**Success (200 OK)**
```json
{
  "message": "리딤코드가 성공적으로 검증되었습니다.",
  "is_valid": true
}
```

**Error (400 Bad Request - Already Used)**
```json
{
  "message": "이미 사용된 리딤코드입니다.",
  "is_valid": false
}
```

**Error (404 Not Found - Invalid Code/Email)**
```json
{
  "message": "유효하지 않은 이메일 또는 리딤코드입니다.",
  "is_valid": false
}
```
