# GitHub Actions 자동 배포 설정 가이드

GitHub Actions를 사용하여 `main` 브랜치에 푸시될 때마다 우분투 서버에 자동으로 배포하는 방법입니다.

## 1. 워크플로우 파일 생성
`.github/workflows/deploy.yml` 파일이 생성되었습니다. 이 파일은 `main` 브랜치에 푸시가 발생하면 SSH를 통해 서버에 접속하여 배포 스크립트를 실행합니다.

## 2. GitHub Secrets 설정
GitHub 저장소의 **Settings > Secrets and variables > Actions** 메뉴에서 `New repository secret`을 클릭하여 다음 변수들을 등록해야 합니다.

| Name | Value | 설명 |
|------|-------|------|
| `HOST` | `123.45.67.89` | 서버의 IP 주소 또는 도메인 |
| `USERNAME` | `ubuntu` | SSH 접속 사용자명 |
| `SSH_PRIVATE_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----...` | SSH 접속용 개인키 (PEM 형식) |
| `PORT` | `22` | SSH 포트 (기본값 22) |
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/...` | 슬랙 알림용 웹훅 URL |

## 3. 서버 설정 (중요)
GitHub Actions가 `sudo systemctl restart` 명령어를 실행하려면, 비밀번호 입력 없이 `sudo`를 사용할 수 있도록 설정해야 합니다.

1. 서버에서 `sudo visudo` 실행
2. 파일 끝에 다음 줄 추가 (사용자명이 `ubuntu`인 경우):
   ```
   ubuntu ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart gunicorn
   ```
   *주의: 보안을 위해 특정 명령어(`restart gunicorn`)에 대해서만 권한을 허용하는 것이 좋습니다.*

## 4. 배포 스크립트 경로 확인
`.github/workflows/deploy.yml` 파일 내의 `script` 부분에서 프로젝트 경로(`cd ...`)와 서비스명(`gunicorn`)이 실제 서버 환경과 일치하는지 확인하고 수정해주세요.

```yaml
script: |
  cd /home/ubuntu/quiz_server  # 실제 프로젝트 경로로 수정
  git pull origin main
  uv sync
  uv run python manage.py migrate
  uv run python manage.py collectstatic --noinput
  sudo systemctl restart gunicorn        # 실제 서비스명으로 수정
```

## 5. 서버 사전 준비 (uv 설치)
서버에 `uv`가 설치되어 있어야 합니다.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
