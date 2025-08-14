import os
import sys
import img2pdf
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime

# ======== CONFIG ========
BASE_SAVE = os.path.expanduser("~/storage/documents/Potentia")

# Check storage access before starting
if not os.path.exists(BASE_SAVE):
    print(f"⚠️ Save path not found: {BASE_SAVE}")
    print("   Run `termux-setup-storage` and try again.")
    sys.exit(1)

os.makedirs(BASE_SAVE, exist_ok=True)

COMMON_DIRS = [
    os.path.expanduser("~/storage/downloads"),
    os.path.expanduser("~/storage/pictures"),
    os.path.expanduser("~/storage/dcim"),
]

# ======== HELPERS ========
def safe_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\n❌ Cancelled.")
        sys.exit(0)

def resolve_path(user_input):
    """Try to resolve user input to a valid file path."""
    if os.path.exists(user_input):
        return user_input
    # Search common dirs
    for d in COMMON_DIRS:
        possible = os.path.join(d, user_input)
        if os.path.exists(possible):
            return possible
    return None

def watermark_image(image_path, watermark_text):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    font_size = int(min(img.size) / 25)

    # Try multiple font paths
    font_paths = [
        "/data/data/com.termux/files/usr/share/fonts/DejaVuSans.ttf",
        "/system/fonts/Roboto-Regular.ttf"
    ]
    font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except:
                pass
    if not font:
        font = ImageFont.load_default()

    text_w, text_h = draw.textsize(watermark_text, font=font)
    pos = (img.width - text_w - 20, img.height - text_h - 10)
    draw.text(pos, watermark_text, font=font, fill=(120, 120, 120))
    return img

# ======== FEATURES ========
def convert_images_to_pdf():
    try:
        print("\n📂 Enter image filenames or full paths (one per line). Type 'done' when finished:")
        files = []
        while True:
            f = safe_input("> ").strip()
            if f.lower() == "done":
                break
            resolved = resolve_path(f)
            if resolved and resolved.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                files.append(resolved)
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

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(BASE_SAVE, f"converted_{len(files)}pages_{ts}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(temp_images))

        for t in temp_images:
            os.remove(t)

        print(f"✅ PDF saved to: {pdf_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

def merge_pdfs():
    try:
        print("\n📂 Enter PDF filenames or full paths to merge (one per line). Type 'done' when finished:")
        files = []
        while True:
            f = safe_input("> ").strip()
            if f.lower() == "done":
                break
            resolved = resolve_path(f)
            if resolved and resolved.lower().endswith(".pdf"):
                files.append(resolved)
            else:
                print("⚠️ Not a valid PDF path.")
        if len(files) < 2:
            print("❌ Need at least 2 PDFs to merge.")
            return

        merged = fitz.open()
        for pdf in files:
            with fitz.open(pdf) as mfile:
                merged.insert_pdf(mfile)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(BASE_SAVE, f"merged_{ts}.pdf")
        merged.save(save_path)
        print(f"✅ Merged PDF saved to: {save_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

def split_pdf():
    try:
        pdf_path = resolve_path(safe_input("📂 Enter PDF filename or path to split: ").strip())
        if not pdf_path:
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

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(BASE_SAVE, f"split_{ts}.pdf")
        new_pdf.save(save_path)
        print(f"✅ Split PDF saved to: {save_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

def compress_pdf():
    try:
        pdf_path = resolve_path(safe_input("📂 Enter PDF filename or path to compress: ").strip())
        if not pdf_path:
            print("❌ File not found.")
            return
        pdf = fitz.open(pdf_path)
        for page in pdf:
            pix = page.get_pixmap(dpi=100)
            page.clean_contents()
            img_pdf = fitz.open()
            img_pdf.insert_page(-1, width=page.rect.width, height=page.rect.height)
            img_pdf[-1].insert_image(page.rect, pixmap=pix)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(BASE_SAVE, f"compressed_{ts}.pdf")
        pdf.save(save_path, deflate=True)
        print(f"✅ Compressed PDF saved to: {save_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

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
