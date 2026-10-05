# posts

게시물 한 건 = 폴더 한 개. 폴더 이름은 `YYYY-MM-DD-brief` 또는 `YYYY-MM-DD-deepdive`.

| 파일 | 내용 |
|---|---|
| 01.jpg ~ NN.jpg | 카드 이미지 (JPEG, 1080×1350, 2~10장) |
| caption.txt | 인스타 캡션 전문 |
| post.json | `{"type": "brief" 또는 "deepdive", "date": "YYYY-MM-DD", "slides": ["01.jpg", ...], "dry_run": false}` |
| published.json | 게시 후 자동 생성 (게시물 ID·링크). 이 파일이 있으면 다시 게시하지 않는다 |

post.json 을 올리면 "인스타 게시" 작업이 시작되고, 승인 후 게시된다.
