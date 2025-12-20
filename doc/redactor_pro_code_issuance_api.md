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
- **Headers**:
    - `X-Redeem-Api-Key`: `16자리 랜덤 문자열` (필수)

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
  "message": "유효한 이메일 주소를 입력하십시오.",
  "error_code": 3003
}
```

**Error (403 Forbidden)**
```json
{
  "message": "권한이 없습니다.",
  "error_code": 1002
}
```

---

## 2. 리딤코드 검증 및 사용 (Validate Code)

이메일, 리딤코드, UUID를 입력받아 유효성을 검증하고 사용 처리합니다.
- **최초 사용**: 코드가 유효하고 사용되지 않은 경우, 현재 기기(UUID)에 바인딩하고 사용 처리(`is_used=True`)합니다.
- **기기 변경 (License Transfer)**: 이미 사용된 코드지만 입력된 UUID가 기존 바인딩된 UUID와 다른 경우, 새로운 기기로 바인딩을 변경하고 성공 응답을 반환합니다. (기존 기기에서는 Pro 기능 비활성화 예상)
- **재검증**: 이미 사용된 코드이고 UUID도 동일한 경우, 성공 응답을 반환합니다.
- **유효하지 않음**: 이메일과 코드가 일치하지 않거나 없는 경우 실패 응답을 반환합니다.

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
| `uuid` | string | Yes | 기기 고유 식별자 (UUID) |

**Example:**
```json
{
  "email": "user@example.com",
  "code": "AB12CD34",
  "uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 응답 (Response)

**Success (200 OK - Verified/Registered)**
```json
{
  "message": "리딤코드가 성공적으로 검증되었습니다.",
  "is_valid": true
}
```

**Success (200 OK - License Transferred)**
```json
{
  "message": "새로운 기기에서 리딤코드를 등록합니다. 기존 기기에 설치된 앱은 pro 기능이 비활성화 됩니다.",
  "is_valid": true
}
```

## 에러 코드 (Error Codes)

| 에러 코드 | HTTP 상태 | 설명 |
| :--- | :--- | :--- |
| **1002** | 403 Forbidden | API Key (`X-Redeem-Api-Key`) 검증 실패 |
| **3003** | 400 Bad Request | 유효하지 않은 데이터 형식 (이메일 누락 등) |
| **4001** | 400 Bad Request | **삭제됨**: 이미 삭제 처리된 리딤코드 |
| **4002** | 404 Not Found | **유효하지 않음**: DB에 존재하지 않는 이메일/코드 조합 |

### 에러 응답 예시

**Error (403 Forbidden)**
```json
{
  "message": "권한이 없습니다.",
  "error_code": 1002
}
```

**Error (400 Bad Request - Deleted)**
```json
{
  "message": "삭제된 리딤코드입니다.",
  "is_valid": false,
  "error_code": 4001
}
```

**Error (404 Not Found - Invalid)**
```json
{
  "message": "유효하지 않은 이메일 또는 리딤코드입니다.",
  "is_valid": false,
  "error_code": 4002
}
```
