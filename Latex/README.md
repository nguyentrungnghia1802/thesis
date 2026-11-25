# Bản LaTeX của khóa luận

Bản này được chuyển từ [thesis - fixx.docx](../thesis%20-%20fixx.docx) ở commit `61ff2b7`. Tệp chính là `thesis-fixx.tex`, còn `figures/` chứa ảnh dùng trong tài liệu. Mục lục, danh mục hình và danh mục bảng được cập nhật khi biên dịch.

Từ thư mục `Latex`, chạy lệnh sau với TeX Live hoặc MiKTeX có XeLaTeX và latexmk.

```sh
latexmk -xelatex -outdir=build thesis-fixx.tex
```

PDF được tạo ở `build/thesis-fixx.pdf`. Trên Overleaf, tải lên tệp `thesis-fixx.tex` cùng thư mục `figures/`, đặt tệp chính là `thesis-fixx.tex` và chọn XeLaTeX.
