# Bản LaTeX của khóa luận

Chỉnh sửa trực tiếp trong `thesis-fixx.tex`. Thư mục `figures/` chứa ảnh minh họa, còn `thesis-fixx.pdf` là bản đã xuất. Mục lục, danh mục hình và danh mục bảng được cập nhật khi biên dịch.

Hình 3.8 dùng ảnh kiểm tra bất biến và ảnh quyết định từ phiên TN03 `d6df3077`, đối chiếu với ảnh chụp trạng thái tại checkpoint 3. [Bằng chứng TN03](../Bang-chung-hinh-USE-20261125-100422/counterbase/).

Từ thư mục `Latex`, chạy lệnh sau với TeX Live hoặc MiKTeX có XeLaTeX và latexmk.

```sh
latexmk -xelatex -outdir=build thesis-fixx.tex
```

PDF được tạo ở `build/thesis-fixx.pdf`. Trên Overleaf, tải lên `thesis-fixx.tex` cùng thư mục `figures/`, đặt `thesis-fixx.tex` làm tệp chính và chọn XeLaTeX.
