import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pdfminer.high_level import extract_text_to_fp
from io import StringIO
import PyPDF2

class PDFSearcher:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Keyword Searcher")
        self.pdf_files = []

        self.open_button = tk.Button(root, text="フォルダを開く", command=self.open_folder)
        self.open_button.pack(pady=10)

        self.search_button = tk.Button(root, text="キーワード検索", command=self.search_keyword, state=tk.DISABLED)
        self.search_button.pack(pady=10)

    def open_folder(self):
        folder_path = filedialog.askdirectory(parent=self.root)
        if folder_path:
            self.pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
            if self.pdf_files:
                self.search_button.config(state=tk.NORMAL)
                messagebox.showinfo("PDFファイル読み込み", "{}個のPDFファイルを読み込みました。".format(len(self.pdf_files)))
            else:
                messagebox.showinfo("PDFファイルなし", "選択したフォルダにはPDFファイルがありません。")

    def search_keyword(self):
        keyword = simpledialog.askstring("キーワード", "検索するキーワードを入力してください：", parent=self.root)
        if keyword:
            results = self.find_keyword_in_pdfs(keyword)
            if results:
                self.display_results(results, keyword)
            else:
                messagebox.showinfo("結果なし", "'{}' に一致する結果は見つかりませんでした。".format(keyword), parent=self.root)

    def find_keyword_in_pdfs(self, keyword):
        results = []
        for pdf_file in self.pdf_files:
            with open(pdf_file, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    output_string = StringIO()
                    extract_text_to_fp(file, output_string, page_numbers=[page_num])
                    text = output_string.getvalue()
                    if text:
                        lines = text.split('\n')
                        for line_num, line in enumerate(lines):
                            char_idx = line.lower().find(keyword.lower())
                            if char_idx != -1:
                                results.append((pdf_file, page_num + 1, line_num + 1, char_idx + 1, keyword, line))
        return results

    def display_results(self, results, keyword):
        result_window = tk.Toplevel(self.root)
        result_window.title("検索結果")
        text_widget = tk.Text(result_window)
        text_widget.pack(expand=1, fill=tk.BOTH)

        for pdf_file, page_num, line_num, char_idx, word, line in results:
            text_widget.insert(tk.END, f"ファイル: {pdf_file}\nページ: {page_num}\n行: {line_num}\n文字位置: {char_idx}\n")
            start_idx = max(0, char_idx - 21)
            end_idx = min(len(line), char_idx + len(word) + 20)
            pre_text = line[start_idx:char_idx - 1]
            post_text = line[char_idx + len(word):end_idx]
            text_widget.insert(tk.END, pre_text)
            text_widget.insert(tk.END, line[char_idx:char_idx + len(word)], 'highlight')
            text_widget.insert(tk.END, post_text + "\n\n")

        text_widget.tag_config('highlight', background='yellow', foreground='black')

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSearcher(root)
    root.mainloop()
