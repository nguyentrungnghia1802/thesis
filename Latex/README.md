# Bản LaTeX của khóa luận

Chỉnh sửa trực tiếp trong `thesis-fixx.tex`. Thư mục `figures/` chứa ảnh minh họa, còn `thesis-fixx.pdf` là bản đã xuất. Mục lục, danh mục hình và danh mục bảng được cập nhật khi biên dịch.

Hình 2.4 được xuất từ sơ đồ iStar Model của USE với đặc tả Auction đầy đủ. Ba khung của Hình 2.6 được sắp xếp trong OAL State từ dữ liệu của cùng checkpoint 47 và bao phủ đủ 24 liên kết. [Mã USE dùng để xuất hình](https://github.com/nguyentrungnghia1802/use/tree/5b6a3542d22a67c25fdb1768de54d7cfec15781d) · [Dữ liệu checkpoint 47](../Bang-chung-hinh-USE-20261125-100422/auction-layout/checkpoint-47.json).

Hai ảnh giao diện ở Mục 3.1 được chụp trực tiếp trên bản USE 7.5.0 nguyên bản với ví dụ CivilStatusWorld và bản USE–JaCaMo có plugin 1.0.1 khi chạy Auction. [USE 7.5.0](https://github.com/useocl/use/tree/af444c47534c4ef9254f24034757e5a499edf660) · [USE–JaCaMo](https://github.com/nguyentrungnghia1802/use/tree/5b6a3542d22a67c25fdb1768de54d7cfec15781d).

Từ thư mục `Latex`, chạy lệnh sau với TeX Live hoặc MiKTeX có XeLaTeX và latexmk. Cài gói phông `tex-gyre` để dùng TeX Gyre Termes như trong PDF. Nếu thiếu phông này, tài liệu dùng Times New Roman hoặc Liberation Serif tùy hệ thống.

```sh
latexmk -xelatex -outdir=build thesis-fixx.tex
```

PDF được tạo ở `build/thesis-fixx.pdf`. Trên Overleaf, tải lên `thesis-fixx.tex` cùng thư mục `figures/`, đặt `thesis-fixx.tex` làm tệp chính và chọn XeLaTeX.
