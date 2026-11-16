# beanpal-cardnews

빈팔(BeanPal) 커피 카드뉴스를 인스타그램 @beanpal2025 에 게시하는 저장소.
카드뉴스 작성기(월요일 브리프·목요일 딥다이브)가 `posts/` 에 게시물을 올리면, 승인 후 GitHub Actions 가 Instagram 공식 API(Instagram 로그인 방식)로 캐러셀을 게시한다.

이 저장소는 공개 저장소다. 인스타에 공개될 카드 이미지와 캡션만 둔다. 출처 메모·내부 문서·코드는 두지 않는다.

## 흐름
1. 작성기가 `scripts/stage_post.py` 로 `posts/YYYY-MM-DD-<type>/` 를 만들고 push
2. "인스타 게시" 작업 시작 → environment `instagram` 승인 대기 (GitHub 알림)
3. 승인하면 `scripts/publish.py` 가 이미지별 컨테이너 → 캐러셀 컨테이너 → 게시 순으로 실행
4. 게시 기록 `published.json` 이 자동 커밋된다(같은 폴더는 다시 게시하지 않음)

## 최초 설정 (운영자)
1. **승인 단계**: Settings → Environments → `instagram` → Required reviewers 에 본인(chrysaor80) 추가 → Save protection rules.
   이 설정 전에는 게시물을 올리지 않는다.
2. **토큰 등록**: Settings → Secrets and variables → Actions → New repository secret
   - `IG_ACCESS_TOKEN`: Meta 개발자 앱에서 발급한 Instagram 장기 접근 토큰
3. **토큰 자동 갱신(권장)**: GitHub 개인 토큰(Fine-grained, 이 저장소만, 권한 "Secrets: Read and write")을 만들어
   `SECRETS_PAT` 로 등록. 없으면 60일마다 토큰을 직접 다시 발급해야 한다.
4. **확인**: Actions → "토큰 확인" → Run workflow. 계정 이름과 유형이 나오면 성공.
5. **시험 게시**: Actions → "인스타 게시" → Run workflow (시험 실행 체크). 실제 게시 없이 캐러셀 생성까지만 확인.

## 실패했을 때
- Actions 탭에서 실패한 작업을 열면 `[API 오류]` 또는 `[중단]` 줄에 원인이 적혀 있다.
- 같은 폴더를 다시 시도하려면 Actions → "인스타 게시" → Run workflow (시험 실행 체크 해제).
