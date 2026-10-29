# QA 12 GIF mới — bản thử chưa duyệt

Nguồn: `13 charnew/*.gif`, art_source `existing`. Kết quả Forge nằm tại `Asset/Character/forge_pilots/charnew/<id>/clips/animation-clips.json`; mỗi gói có một clip `reference_unclassified`, không khẳng định đó là một động tác hay skill. Các ô dưới là kết quả `qa.checks` của từng file; không có ngưỡng cho `tick_grid` hoặc `loop_seam`. Forge kiểm tra byte copy PNG và timeline WebP, nhưng không thay thế duyệt chuyển động và alpha bằng mắt.

| Nguồn | tick_grid WARN (ms) | near_duplicate_holds WARN (ngưỡng 0) | loop_seam cần duyệt (tỷ lệ) |
|---|---:|---:|---:|
| buffao | 6.667 | — | 1.253544 |
| scosrian | 6.667 | — | 0.595329 |
| dump | — | — | 2.023753 |
| hemsiss | — | 8 | 1.341468 |
| scorpit | 6.667 | — | 0.749647 |
| Domrico | 6.667 | 1 | 2.450969 |
| hecfaom | — | — | 1.101419 |
| Impector | 6.667 | — | 0.338704 |
| Actem | 6.667 | — | 0.861582 |
| Hatomin | 6.667 | — | 0.933595 |
| Trainxoan | 6.667 | — | 1.536363 |
| urguro | 6.667 | — | 0.758020 |

Dấu — nghĩa là kiểm tra đó không WARN; không có nghĩa chuyển động đã được duyệt. `tick_grid` là sai lệch lưới thời gian, không tự chứng minh khựng. `near_duplicate_holds` đánh dấu tư thế gần giống, có thể là giữ chủ ý. Phần nối vòng chỉ là bản xem thử, cần so nguồn trước khi kết luận phải sửa.

Tất cả 12 clip đã được build, song còn cần duyệt nền và chiều cao thân theo frame tham chiếu, cũng như phát 1×/0,5× trên trình duyệt của anh và đo thiết bị. Phân loại clip, animation mới, APK và 60 FPS chưa được xác nhận. Một số frame có phần alpha chạm mép canvas nguồn (buffao 13, scosrian 2, dump 9, hemsiss 5, scorpit 4, Domrico 1, hecfaom 5, Impector 10, urguro 1); đây không phải bằng chứng có thể khôi phục phần hình nằm ngoài GIF.
