# Salad 추천 + Firebase 단체 주문

## 1. Firebase 웹 설정 입력
Firebase Console > 프로젝트 설정 > 일반 > 내 앱 > 웹 앱 > SDK 설정 및 구성에서 값을 복사해 `firebase-config.js`의 `PASTE_...` 항목을 교체합니다.

`databaseURL`은 기존 Realtime Database 주소로 미리 입력되어 있습니다.

## 2. 익명 인증 활성화
Firebase Console > Authentication > Sign-in method > 익명(Anonymous) > 사용 설정

## 3. Realtime Database 규칙 적용
Firebase Console > Realtime Database > 규칙에서 `database.rules.json` 내용을 붙여넣고 게시합니다.

- 기존 룰렛 게임 `/rooms`는 현재처럼 공개 유지됩니다.
- 신규 주문 데이터는 `/saladOrders`에 저장됩니다.

## 4. GitHub 업로드
저장소 루트에 아래 파일을 업로드합니다.

- `index.html`
- `order-admin.html`
- `firebase-config.js`
- `menu-data.js`
- `database.rules.json` (배포에는 필수 아님, 규칙 보관용)

## 5. 이용 방법
1. `order-admin.html` 접속
2. 주문방 생성
3. 참여 링크 복사 및 공유
4. 참여자는 이름을 입력하고 추천 메뉴를 제출
5. 담당자 화면에서 메뉴별/참여자별 실시간 취합
6. 마감 후 주문서 복사 또는 CSV 다운로드

## 주의
`firebase-config.js`의 Firebase 웹 구성값은 웹앱에 포함되는 공개 식별 정보입니다. 데이터 보호는 익명 인증과 Realtime Database Security Rules가 담당합니다. 루트의 `.read: true`, `.write: true` 규칙은 다시 사용하지 마세요.
