---
title: "누아로움(NOUAROUM) 홈페이지 — 배포·운영 안내"
---

# 누아로움 홈페이지 — 배포·운영 안내

2026-11-26 1차 시안 제작·배포했습니다.

## 1. 지금 상태

| 항목 | 값 |
|---|---|
| 접속 주소 | **https://nuaroum-site.vercel.app** |
| GitHub | https://github.com/makjang97-prog/nuaroum-site (public) |
| Vercel 프로젝트 | `nuaroum-site` — 팀 `maisonyoung`, Hobby(무료) |
| 소스 폴더 | `documents/nuaroum-site/` (저장소 루트 = 사이트 루트) |
| 첫 배포 | 2026-11-26 04:2x KST (`a437fed`) |
| 정식 도메인 | `nuaroum.com` / `nuaroum.co.kr` — 가비아 가상계좌 38,500원 입금 후 연결 |
| 작업 가이드 | `클로드_누아로움_작업가이드.md` (클로드에게 그대로 전달) |

## 2. 고치는 방법

```bash
cd documents/nuaroum-site
# 파일 수정 후
git add -A
git commit -m "문구 수정"
git push        # → Vercel 자동 배포 30초~1분
```

제품만 추가할 때는 `products.json`과 `assets/products/` 사진만 건드리면 됩니다
(`index.html`·`styles.css`는 디자인 파일이라 그대로 둡니다).

## 3. 페이지 구성

1. 상단 바 — `INCHEON · BY APPOINTMENT` / `HERITAGE FINE JEWELRY` / `SINCE 2026`
2. 헤더 — `COLLECTION · BESPOKE · ATELIER` + `NOUAROUM` 워드마크 + `SHOWROOM · RESERVATION`
   (모바일은 햄버거 → 넘버링된 전체 메뉴 드로어)
3. Hero — "빛을 담아, 오래도록" + 제품 컷 `NR-EG-001` + 하단 소재·세공·쇼룸 3항목
4. Brand Story — 반지 상면 컷 + 브랜드 소개 + PT950·HAND SETTING·INCHEON ATELIER
5. Collection — 4칸 카드(WEDDING BAND / ENGAGEMENT / SOLITAIRE / COUPLE RING) + 코드 범위
6. Catalog — `products.json` 기반 제품 그리드 · 카테고리 필터 · 상세 모달(썸네일·스펙·옵션)
7. Bespoke & Care — 다크 섹션, 3가지 가치(1:1 세공 · 평생 케어 · 프라이빗 상담)
8. Showroom — 주소·방문·주차 + OpenStreetMap 약도 + 네이버 지도 링크
9. Reservation — 방문 예약 3단계 + 채널(네이버 예약·전화·방문) 안내
10. Footer — 상호·대표·사업자등록번호·주소 / `SITE PREVIEW · v1`

## 4. 남은 자리 (정식 오픈 전)

1. **전화번호** — 지금은 `정식 오픈 시 안내`. 확정되면 예약 섹션·JSON-LD에 반영.
2. **예약 채널** — 네이버 예약/카카오톡 채널 개설 후 링크 연결.
3. **제품 사진·스펙** — 현재 `NR-EG-001`만 실사진, 나머지는 플레이스홀더 + 예시 스펙.
   `클로드_누아로움_작업가이드.md` 7번 프롬프트로 채웁니다.
4. **커스텀 도메인** — `nuaroum.com` 입금 확인 후 Vercel Domains 연결,
   연결 후 `canonical`·`og:url`·`robots.txt`·`sitemap.xml` 주소 교체.
5. **정책 문구 확인** — `평생 케어·폴리싱`, `SINCE 2026` 표기는 실제 운영 기준 확인 후 확정.

## 5. 검증 기록 (2026-11-26, 실배포 기준)

- HTTP 200: `/`, `/styles.css`, `/script.js`, `/products.json`, 사진 2장, `/assets/map.jpg`,
  `/assets/og-image.jpg`, 폰트 2종, `/robots.txt`, `/sitemap.xml`
- 콘솔 오류 0건 / 실패 요청 0건 / 깨진 이미지 0건
- 가로 넘침 0: 1440 · 768 · 390 · 360px
- 상세 모달 열림·ESC 닫힘, 카테고리 필터(웨딩밴드 3건), 모바일 드로어 열림/링크 이동 후 닫힘
- 캡처: `screenshots/pc-top.png`, `pc-story.png`, `pc-collection.png`, `pc-catalog.png`,
  `pc-bespoke.png`, `pc-showroom.png`, `pc-reservation.png`, `pc-footer.png`, `pc-modal.png`,
  `pc-full.png`, `mobile-top.png`, `mobile-menu.png`, `mobile-catalog.png`, `mobile-showroom.png`,
  `mobile-modal.png`, `mobile-full.png`, `tablet-top.png`, `mobile360-menu.png`

## 6. 참고

- 폰트는 자체 호스팅(Cormorant / Noto Serif KR 서브셋)이라 외부 CDN에 의존하지 않습니다.
- 약도는 OpenStreetMap 타일(© OpenStreetMap contributors)로 만들었고 좌표는 두용프라자 기준입니다.
- `tools/build_assets.py`를 다시 돌리면 사진 리사이즈·약도·OG·폰트가 재생성됩니다(원본 사진 경로 확인).
