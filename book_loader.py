from pypdf import PdfReader

def load_books():
    text = ""

    # PDF file
    pdf_path = "book/book1.pdf"
    reader = PdfReader(pdf_path)

    for page in reader.pages:
        text += page.extract_text() or ""

    # TEXT file
    txt_path = "book/book2.txt"
    with open(txt_path, "r", encoding="utf-8") as f:
        text += "\n" + f.read()

    return text