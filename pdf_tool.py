import os
import sys
import img2pdf
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
from pathlib import Path

# ======== CONFIG ========
BASE_SAVE = "/storage/emulated/0/Documents/Potentia"
os.makedirs(BASE_SAVE, exist_ok=True)

# ======== HELPERS ========
def safe_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\n❌ Cancelled.")
        sys.exit(0)

def watermark_image(image_path, watermark_text):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    font_size = int(min(img.size) / 25)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()
    text_w, text_h = draw.textsize(watermark_text, font=font)
    pos = (img.width - text_w - 20, img.height - text_h - 10)
    draw.text(pos, watermark_text, font=font, fill=(120, 120, 120))
    return img

def convert_images_to_pdf():
    print("\n📂 Enter full paths to images (one per line). Type 'done' when finished:")
    files = []
    while True:
        f = safe_input("> ").strip()
        if f.lower() == "done":
            break
        if os.path.exists(f) and f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            files.append(f)
        else:
            print("⚠️ Not a valid image path.")
    if not files:
        print("❌ No images selected.")
        return

    name = safe_input("✏️ Enter your name for watermark: ").strip()
    wm_text = f"Prepared by {name}"

    temp_images = []
    for img_path in files:
        img = watermark_image(img_path, wm_text)
        temp_path = img_path + "_wmtemp.jpg"
        img.save(temp_path, "JPEG")
        temp_images.append(temp_path)

    pdf_path = os.path.join(BASE_SAVE, f"converted_{len(files)}pages.pdf")
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(temp_images))

    for t in temp_images:
        os.remove(t)

    print(f"✅ PDF saved to: {pdf_path}")

def merge_pdfs():
    print("\n📂 Enter full paths to PDFs to merge (one per line). Type 'done' when finished:")
    files = []
    while True:
        f = safe_input("> ").strip()
        if f.lower() == "done":
            break
        if os.path.exists(f) and f.lower().endswith(".pdf"):
            files.append(f)
        else:
            print("⚠️ Not a valid PDF path.")
    if len(files) < 2:
        print("❌ Need at least 2 PDFs to merge.")
        return

    merged = fitz.open()
    for pdf in files:
        with fitz.open(pdf) as mfile:
            merged.insert_pdf(mfile)

    save_path = os.path.join(BASE_SAVE, "merged.pdf")
    merged.save(save_path)
    print(f"✅ Merged PDF saved to: {save_path}")

def split_pdf():
    pdf_path = safe_input("📂 Enter PDF path to split: ").strip()
    if not os.path.exists(pdf_path):
        print("❌ File not found.")
        return
    ranges = safe_input("✏️ Enter page ranges (e.g., 1-3,5,7-9): ").strip()
    pages = []
    for part in ranges.split(","):
        if "-" in part:
            start, end = map(int, part.split("-"))
            pages.extend(range(start - 1, end))
        else:
            pages.append(int(part) - 1)

    pdf = fitz.open(pdf_path)
    new_pdf = fitz.open()
    for p in pages:
        new_pdf.insert_pdf(pdf, from_page=p, to_page=p)
    save_path = os.path.join(BASE_SAVE, "split.pdf")
    new_pdf.save(save_path)
    print(f"✅ Split PDF saved to: {save_path}")

def compress_pdf():
    pdf_path = safe_input("📂 Enter PDF path to compress: ").strip()
    if not os.path.exists(pdf_path):
        print("❌ File not found.")
        return
    pdf = fitz.open(pdf_path)
    for page in pdf:
        pix = page.get_pixmap(dpi=100)
        page.clean_contents()
        img_pdf = fitz.open()
        img_pdf.insert_page(-1, width=page.rect.width, height=page.rect.height)
        img_pdf[-1].insert_image(page.rect, pixmap=pix)
    save_path = os.path.join(BASE_SAVE, "compressed.pdf")
    pdf.save(save_path, deflate=True)
    print(f"✅ Compressed PDF saved to: {save_path}")

# ======== MAIN ========
def main():
    while True:
        print("\n==== POTENTIA PDF TOOL ====")
        print("1️⃣ Convert Images to PDF (with watermark)")
        print("2️⃣ Merge PDFs")
        print("3️⃣ Split PDF")
        print("4️⃣ Compress PDF")
        print("0️⃣ Exit")

        choice = safe_input("Select: ").strip()
        if choice == "1":
            convert_images_to_pdf()
        elif choice == "2":
            merge_pdfs()
        elif choice == "3":
            split_pdf()
        elif choice == "4":
            compress_pdf()
        elif choice == "0":
            print("👋 Bye.")
            break
        else:
            print("⚠️ Invalid choice.")

if __name__ == "__main__":
    main()
