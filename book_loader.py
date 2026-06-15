from pypdf import PdfReader

def load_books():
    text = ""

    # load PDF
    reader = PdfReader("book/book1.pdf")
    for page in reader.pages:
        text += page.extract_text() or ""

    # load TXT (optional second file)
    with open("book/book2.txt", "r", encoding="utf-8") as f:
        text += "\n" + f.read()

    return text