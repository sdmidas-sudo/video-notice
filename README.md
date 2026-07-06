# 영상공고

영상 제작 공고를 자동으로 모아 정리하는 앱 프로젝트입니다.

## 1차 목표

앱을 켜면 주요 사이트 6곳을 확인하고, 바우처 영상, 홈쇼핑/인서트 영상, 모바일 라이브/라이브커머스 관련 공고를 골라 링크와 요약을 보여줍니다.

## 앱 컨셉

- 이름: 영상공고
- 아이콘 방향: 돋보기 + 영상/재생 느낌
- 1차 형태: 모바일에서도 볼 수 있는 웹앱
- 핵심 기능: 자동 검색, 관련도 분류, 요약, 원문 링크 제공

## 1차 감시 사이트

1. TRN 쇼핑엔티 사업공고
   - https://www.trncompany.co.kr/hp/noticeHomeList.do
2. 현대홈쇼핑 입찰/공지
   - https://company.hmall.com/news/news_notice.html
3. 나라장터
   - https://www.g2b.go.kr/
4. 기업마당 지원사업 공고
   - https://www.bizinfo.go.kr/sii/siia/selectSIIA200View.do
5. 중소벤처24 사업공고
   - https://www.smes.go.kr/main/sportsBsnsPolicy
6. 수출바우처 공지사항
   - https://www.exportvoucher.com/portal/board/boardList

## 검색 키워드

- 바우처 영상: 홍보영상, 제품영상, 수출바우처, 혁신바우처, 마케팅 바우처, 콘텐츠 제작, 동영상 제작
- 인서트/홈쇼핑: 홈쇼핑, 인서트, 상품소개영상, TV홈쇼핑, 방송영상, 제품 시연영상
- 모바일 라이브: 라이브커머스, 모바일 라이브, 디지털커머스, 소담스퀘어, 온라인 판로, 쇼핑라이브
- 입찰형: 영상 제작 용역, 홍보물 제작, 콘텐츠 제작 용역, 촬영 편집, SNS 영상

## 화면 초안

- 상단: 영상공고
- 주요 버튼: 새로 검색
- 탭: 전체, 바우처, 홈쇼핑/인서트, 라이브커머스, 입찰
- 공고 카드: 제목, 관련도, 요약, 마감일, 출처 사이트, 원문 링크

## 다음 작업

1. 6개 사이트별 자동 검색 가능 방식 확인
2. 검색 결과 수집용 1차 프로토타입 만들기
3. 관련도 분류 규칙 만들기
4. 웹앱 화면 만들기
5. GitHub에 계속 저장하면서 노트북/데스크톱에서 이어 작업

## 현재 프로토타입

- `index.html`: 모바일에서도 볼 수 있는 웹앱 첫 화면
- `styles.css`: 기본 화면 스타일
- `app.js`: 실제 수집 결과 JSON 표시, 검색, 탭 필터
- `scripts/collect_notices.py`: 6개 사이트를 확인해 키워드가 감지된 공고만 `data/notices.json`, `data/notices.js`로 저장

수집 갱신:

```powershell
& 'C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\collect_notices.py
```

그 다음 브라우저에서 `index.html`을 열면 감지된 공고와 원문 링크를 확인할 수 있습니다.

## 자동 검색과 휴대폰 알림

- GitHub Actions가 매일 오전 9시(한국시간)에 수집 스크립트를 실행합니다.
- 검색어: 영상, 영상제작, 인서트, 홍보영상, 홍보영화, 숏폼, 롱폼, 유튜브
- 새 공고가 감지되면 `NTFY_TOPIC` 저장소 Secret으로 휴대폰 푸시 알림을 보냅니다.
- 휴대폰에서 ntfy 앱을 설치하고, 직접 정한 토픽 이름을 구독한 뒤 GitHub 저장소 Secret `NTFY_TOPIC`에 같은 값을 넣으면 됩니다.
