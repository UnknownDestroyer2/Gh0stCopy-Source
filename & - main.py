import os
import sys
import time
import platform
import subprocess
import tkinter as tk
import warnings
from tkinter import scrolledtext, messagebox
from fpdf import FPDF


try:
    import win32print
except ImportError:
    win32print = None

warnings.filterwarnings("ignore", category=DeprecationWarning)

def find_ghostscript():
    base_paths = [
        r"C:\Program Files\gs",
        r"C:\Program Files (x86)\gs"
    ]
    for base in base_paths:
        if os.path.exists(base):
            versions = [d for d in os.listdir(base) if d.startswith('gs')]
            versions.sort(reverse=True)
            for ver in versions:
                path_64 = os.path.join(base, ver, "bin", "gswin64c.exe")
                path_32 = os.path.join(base, ver, "bin", "gswin32c.exe")
                if os.path.isfile(path_64):
                    return path_64
                elif os.path.isfile(path_32):
                    return path_32
    return None

GS_PATH = find_ghostscript()

class PDF(FPDF):
    def header(self):
        self.set_font("Ubuntu-B", "", 5)
        self.cell(0, 10, "Kağıdı size uygun şekilde kesin!", 0, 1, "C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Ubuntu-B", "", 4)
        self.cell(0, 10, f"Sayfa {self.page_no()}", 0, 0, "C")

def print_with_ghostscript(pdf_file, printer_name):
    if GS_PATH is None:
        print("[-] Ghostscript bulunamadı, yazdırma iptal.")
        return False
    cmd = [
        GS_PATH,
        "-dBATCH",
        "-dNOPAUSE",
        "-dNOPROMPT",
        "-sDEVICE=mswinpr2",
        f"-sOutputFile=%printer%{printer_name}",
        pdf_file
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"\n[-] Ghostscript yazdırma hatası: {e}")
        return False

def generate_pdf(text, filename):
    pdf = PDF()
    # Fontu ekle bi kere baştan
    pdf.add_font("Ubuntu-B", "", "Ubuntu-B.ttf", uni=True)
    pdf.add_page()
    pdf.set_font("Ubuntu-B", "", 5)

    pdf.multi_cell(0, 2, text)
    pdf.output(filename)
    print(f"[+] PDF '{filename}' başarıyla oluşturuldu!")

    if platform.system() != "Windows" or not win32print:
        print("-- Windows değil ya da pywin32 yok, yazdırma atlandı.")
        return

    try:
        printer = win32print.GetDefaultPrinter()
    except Exception:
        printer = None

    if not printer:
        print("-- Varsayılan yazıcı bulunamadı, yazdırma atlandı.")
        return

    print(f"-- '{printer}' yazıcısına gönderiliyor...")
    if print_with_ghostscript(filename, printer):
        print("[+] Yazdırma tamamlandı!")
    else:
        print("[-] Yazdırılamadı! Ghostscript fail verdi!")

def on_save():
    text = txt.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Uyarı", "Ea metin boş amk!")
        return
    fn = file_name.get().strip()
    if not fn.endswith(".pdf"):
        fn += ".pdf"
    root.destroy()
    generate_pdf(text, fn)
    messagebox.showinfo("Bitti", f"{fn} yazıcıdan çıkıyor amk!")

if __name__ == "__main__":
    fname = input("Dosya adı ne olsun lan? (uzantı .pdf ekliyoz): ").strip()
    if not fname:
        print("Hadi ya boş mu bıraktın? Çıkıyorum.")
        sys.exit(1)

    # Ubuntu-B.ttf dosyası aynı klasörde olmalı, yoksa hata verir!

    root = tk.Tk()
    root.title("PDF Metin Yapıştır")
    root.geometry("600x600")

    tk.Label(root, text="Metni buraya yapıştır, sonra Kaydet'e bas:", font=("Arial", 10)).pack(pady=5)
    txt = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 10))
    txt.pack(expand=True, fill='both', padx=10, pady=(5, 50))

    frm = tk.Frame(root)
    frm.pack(pady=5)
    tk.Label(frm, text="Dosya Adı:", font=("Arial", 9)).pack(side=tk.LEFT)
    file_name = tk.Entry(frm, width=30, font=("Arial", 9))
    file_name.insert(0, fname)
    file_name.pack(side=tk.LEFT, padx=5)

    tk.Button(root, text="Kaydet ve Yazdır", command=on_save, font=("Arial", 12), height=2).pack(pady=10)

    root.mainloop()
