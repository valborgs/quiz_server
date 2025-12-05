# quiz_server

## Features

### Redeem Code Issuance (redactor_pro_code_issuance)
- **API**: `POST /api/redeem/issue/` to issue or retrieve 8-digit redeem codes for an email.
- **Dashboard**: Web interface at `/api/redeem/dashboard/` for manual code issuance.
- **Model**: `RedeemCode` stores unique email and code pairs.