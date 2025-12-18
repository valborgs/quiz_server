// API 설정
const API_BASE_URL = 'https://comon.dev/api';
const ITEMS_PER_PAGE = 5;

// 다국어 번역 데이터
const translations = {
    ko: {
        donation_msg: "이 개발자에게는 커피가 필요해요.",
        donation_msg_sub: "This developer needs a coffee.",
        guestbook_title: "방명록",
        guestbook_subtitle: "Guestbook",
        name_placeholder: "이름 (미입력시 익명)",
        password_placeholder: "비밀번호 (삭제용)",
        content_placeholder: "응원의 메시지를 남겨주세요! (최대 4줄)",
        submit_btn: "✨ 등록하기",
        modal_title: "🔐 비밀번호 확인",
        modal_password_placeholder: "비밀번호를 입력하세요",
        modal_cancel: "취소",
        modal_delete: "삭제",
        empty_message: "아직 작성된 방명록이 없습니다.<br>첫 번째 메시지를 남겨보세요! 💬",
        error_unavailable: "현재 방명록을 사용할 수 없습니다.",
        alert_content_required: "내용을 입력해주세요!",
        alert_password_required: "비밀번호를 입력해주세요! (삭제 시 필요)",
        alert_enter_password: "비밀번호를 입력해주세요!",
        alert_not_found: "해당 글을 찾을 수 없습니다.",
        alert_wrong_password: "비밀번호가 일치하지 않습니다!"
    },
    en: {
        donation_msg: "This developer needs a coffee.",
        donation_msg_sub: "Please support me!",
        guestbook_title: "Guestbook",
        guestbook_subtitle: "",
        name_placeholder: "Name (Anonymous if empty)",
        password_placeholder: "Password (for deletion)",
        content_placeholder: "Leave a message! (Max 4 lines)",
        submit_btn: "✨ Submit",
        modal_title: "🔐 Password Required",
        modal_password_placeholder: "Enter password",
        modal_cancel: "Cancel",
        modal_delete: "Delete",
        empty_message: "No messages yet.<br>Be the first to leave a message! 💬",
        error_unavailable: "Guestbook is currently unavailable.",
        alert_content_required: "Please enter a message!",
        alert_password_required: "Please enter a password! (Required for deletion)",
        alert_enter_password: "Please enter the password!",
        alert_not_found: "Message not found.",
        alert_wrong_password: "Incorrect password!"
    }
};

// 상태 관리
let currentLang = detectLanguage();
let currentPage = 1;
let totalCount = 0;
let deleteTargetId = null;
let isLoading = false;

// 시스템/브라우저 언어 감지
function detectLanguage() {
    const savedLang = localStorage.getItem('preferredLanguage');
    if (savedLang) return savedLang;

    const browserLang = navigator.language || navigator.userLanguage;
    return browserLang.startsWith('ko') ? 'ko' : 'en';
}

// 언어 토글
function toggleLanguage() {
    currentLang = currentLang === 'ko' ? 'en' : 'ko';
    localStorage.setItem('preferredLanguage', currentLang);
    applyLanguage();
}

// 언어 적용
function applyLanguage() {
    const trans = translations[currentLang];

    document.getElementById('langText').textContent = currentLang === 'ko' ? 'EN' : '한국어';

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (trans[key] !== undefined) {
            el.innerHTML = trans[key];
        }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (trans[key]) {
            el.placeholder = trans[key];
        }
    });

    loadGuestbook();
}

// 번역 가져오기
function t(key) {
    return translations[currentLang][key] || key;
}

// 날짜 포맷팅
function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}.${month}.${day} ${hours}:${minutes}`;
}

// HTML 이스케이프
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 로딩 표시
function showLoading() {
    const listContainer = document.getElementById('guestbookList');
    listContainer.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
}

// 방명록 목록 조회 (API)
async function loadGuestbook() {
    const listContainer = document.getElementById('guestbookList');
    const paginationContainer = document.getElementById('pagination');

    if (!API_BASE_URL) {
        listContainer.innerHTML = `<div class="error-message">${t('error_unavailable')}</div>`;
        paginationContainer.innerHTML = '';
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/guestbook/?page=${currentPage}&page_size=${ITEMS_PER_PAGE}`);

        if (!response.ok) {
            throw new Error('API request failed');
        }

        const data = await response.json();
        totalCount = data.count;

        renderGuestbook(data.results);
        renderPagination();
    } catch (error) {
        console.error('Failed to load guestbook:', error);
        listContainer.innerHTML = `<div class="error-message">${t('error_unavailable')}</div>`;
        paginationContainer.innerHTML = '';
    }
}

// 방명록 렌더링
function renderGuestbook(entries) {
    const listContainer = document.getElementById('guestbookList');

    if (!entries || entries.length === 0) {
        listContainer.innerHTML = `<div class="empty-message">${t('empty_message')}</div>`;
        return;
    }

    listContainer.innerHTML = entries.map(entry => `
        <div class="guestbook-item">
            <button class="delete-btn" onclick="openDeleteModal(${entry.id})" title="${currentLang === 'ko' ? '삭제' : 'Delete'}">✕</button>
            <div class="guestbook-header">
                <span class="guestbook-author">${escapeHtml(entry.name)}</span>
                <span class="guestbook-date">· ${formatDate(entry.created_at)}</span>
            </div>
            <div class="guestbook-content">${escapeHtml(entry.content)}</div>
        </div>
    `).join('');
}

// 페이징 렌더링
function renderPagination() {
    const paginationContainer = document.getElementById('pagination');
    const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);

    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }

    let paginationHTML = `<button class="page-btn" onclick="goToPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>◀</button>`;

    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }

    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }

    paginationHTML += `<button class="page-btn" onclick="goToPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>▶</button>`;

    paginationContainer.innerHTML = paginationHTML;
}

// 페이지 이동
function goToPage(page) {
    const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadGuestbook();
}

// 방명록 작성 (API)
async function submitGuestbook() {
    if (!API_BASE_URL) {
        alert(t('error_unavailable'));
        return;
    }

    const nameInput = document.getElementById('guestName');
    const passwordInput = document.getElementById('guestPassword');
    const contentInput = document.getElementById('guestContent');
    const submitBtn = document.getElementById('submitBtn');

    let name = nameInput.value.trim();
    const password = passwordInput.value.trim();
    let content = contentInput.value.trim();

    // 최대 4줄로 제한
    const lines = content.split('\n');
    if (lines.length > 4) {
        content = lines.slice(0, 4).join('\n');
    }

    if (!content) {
        alert(t('alert_content_required'));
        return;
    }

    if (!password) {
        alert(t('alert_password_required'));
        return;
    }

    // 이름 20자 제한
    if (name.length > 20) {
        name = name.substring(0, 20);
    }

    submitBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/guestbook/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name || '',
                password: password,
                content: content
            })
        });

        if (!response.ok) {
            throw new Error('API request failed');
        }

        // 입력 필드 초기화
        nameInput.value = '';
        passwordInput.value = '';
        contentInput.value = '';
        document.getElementById('charCount').textContent = '0';

        // 첫 페이지로 이동 후 새로고침
        currentPage = 1;
        loadGuestbook();
    } catch (error) {
        console.error('Failed to submit guestbook:', error);
        alert(t('error_unavailable'));
    } finally {
        submitBtn.disabled = false;
    }
}

// 삭제 모달 열기
function openDeleteModal(id) {
    deleteTargetId = id;
    document.getElementById('deletePassword').value = '';
    document.getElementById('deleteModal').classList.add('show');
}

// 삭제 모달 닫기
function closeDeleteModal() {
    deleteTargetId = null;
    document.getElementById('deleteModal').classList.remove('show');
}

// 삭제 확인 (API)
async function confirmDelete() {
    if (!API_BASE_URL) {
        alert(t('error_unavailable'));
        closeDeleteModal();
        return;
    }

    const password = document.getElementById('deletePassword').value;
    const confirmBtn = document.getElementById('confirmDeleteBtn');

    if (!password) {
        alert(t('alert_enter_password'));
        return;
    }

    confirmBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/guestbook/${deleteTargetId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                password: password
            })
        });

        if (response.status === 204) {
            closeDeleteModal();
            loadGuestbook();
            return;
        }

        if (response.status === 404) {
            alert(t('alert_not_found'));
            closeDeleteModal();
            loadGuestbook();
            return;
        }

        const data = await response.json();

        if (data.error === 'password_mismatch') {
            alert(t('alert_wrong_password'));
            return;
        }

        throw new Error('API request failed');
    } catch (error) {
        console.error('Failed to delete guestbook:', error);
        alert(t('error_unavailable'));
        closeDeleteModal();
    } finally {
        confirmBtn.disabled = false;
    }
}

// 글자 수 카운터
document.getElementById('guestContent').addEventListener('input', function () {
    const lines = this.value.split('\n');
    if (lines.length > 4) {
        this.value = lines.slice(0, 4).join('\n');
    }
    document.getElementById('charCount').textContent = this.value.length;
});

// 엔터키로 모달 확인
document.getElementById('deletePassword').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        confirmDelete();
    }
});

// 모달 외부 클릭 시 닫기
document.getElementById('deleteModal').addEventListener('click', function (e) {
    if (e.target === this) {
        closeDeleteModal();
    }
});

// 초기화
applyLanguage();

// 보안 및 단축키 설정
document.addEventListener('contextmenu', event => event.preventDefault());
document.addEventListener('dragstart', event => event.preventDefault());
document.addEventListener('selectstart', event => event.preventDefault());
document.addEventListener('keydown', event => {
    if (
        event.key === 'F12' ||
        (event.ctrlKey && event.shiftKey && ['I', 'J', 'C'].includes(event.key.toUpperCase())) ||
        (event.ctrlKey && event.key.toUpperCase() === 'U')
    ) {
        event.preventDefault();
    }
});
