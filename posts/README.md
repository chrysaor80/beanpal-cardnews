# posts

게시물 한 건 = 폴더 한 개. 폴더 이름은 `YYYY-MM-DD-brief` 또는 `YYYY-MM-DD-deepdive`.

| 파일 | 내용 |
|---|---|
| 01.jpg ~ NN.jpg | 카드 이미지 (JPEG, 1080×1350, 2~10장) |
| caption.txt | 인스타 캡션 전문 |
| post.json | `{"type": "brief" 또는 "deepdive", "date": "YYYY-MM-DD", "slides": ["01.jpg", ...], "dry_run": false}` (+ 선택 `"publish_at": "YYYY-MM-DDTHH:MM+09:00"`) |
| approved.json | 예약 게시 폴더를 승인했을 때 자동 생성 (승인한 실행 번호·커밋). 예약 시각에 이 기록을 검증하고 게시 |
| published.json | 게시 후 자동 생성 (게시물 ID·링크). 이 파일이 있으면 다시 게시하지 않는다 |

post.json 을 올리면 "인스타 게시" 작업이 시작되고, 승인 후 게시된다. publish_at 이 있으면 승인 후 그 시각에 "인스타 예약 게시" 작업이 게시한다.
