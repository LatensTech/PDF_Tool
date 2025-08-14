#!/data/data/com.termux/files/usr/bin/bash

echo "🔧 Bootstrapping Potentia PDF Tool..."
sleep 2

# ✅ Update system
pkg update -y
pkg install python termux-api -y

# Python dependencies for PDF tool
DEPS=("pillow" "img2pdf" "pymupdf")
for dep in "${DEPS[@]}"; do
    if ! python3 -c "import $dep" &> /dev/null; then
        echo "📦 Installing Python module: $dep..."
        pip install $dep
    else
        echo "✅ Python module '$dep' already installed."
    fi
done


sleep 1

# 📁 Create Potentia base dirs
mkdir -p ~/potentia/drops
mkdir -p ~/potentia/config
mkdir -p ~/potentia/logs

echo "$(date) - Checked Python dependencies" >> ~/potentia/logs/potentia.log

# Move drop into place
CURRENT_DIR=$(pwd)
DROP_DEST=~/potentia/drops/pdf_tool
rm -rf "$DROP_DEST"
mkdir -p "$DROP_DEST"
cp -r "$CURRENT_DIR"/* "$DROP_DEST"

# Ensure log exists
touch ~/potentia/logs/potentia.log
touch "$DROP_DEST/pdf_tool.log"

# ⚙️ Create/update Potentia config
CONFIG_FILE=~/potentia/config/potentia.env
if [ ! -f "$CONFIG_FILE" ]; then
    echo "# Potentia Config" > "$CONFIG_FILE"
    echo "PDFTOOL_ENABLED=true" >> "$CONFIG_FILE"
    echo "INSTALL_DATE=$(date)" >> "$CONFIG_FILE"
else
    sed -i "s/PDFTOOL_ENABLED=.*/PDFTOOL_ENABLED=true/" "$CONFIG_FILE" || echo "PDFTOOL_ENABLED=true" >> "$CONFIG_FILE"
fi

# 📂 Check & create storage save path
SAVE_PATH=~/storage/documents/Potentia
if [ ! -d "$SAVE_PATH" ]; then
    mkdir -p "$SAVE_PATH" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "⚠️ Storage not accessible. Run: termux-setup-storage"
        echo "   Then re-run this installer."
    else
        echo "✅ Created save folder at $SAVE_PATH"
    fi
else
    echo "✅ Save folder already exists: $SAVE_PATH"
fi

# 🧙 Add shell alias
PROFILE_FILE=~/.bashrc
ALIAS_CMD='alias pdftool="python3 ~/potentia/drops/pdf_tool/pdf_tool.py"'
grep -qxF "$ALIAS_CMD" "$PROFILE_FILE" || echo "$ALIAS_CMD" >> "$PROFILE_FILE"

ALIAS_ENTER='alias drops="cd ~/potentia/drops/pdf_tool/"'
grep -qxF "$ALIAS_ENTER" "$PROFILE_FILE" || echo "$ALIAS_ENTER" >> "$PROFILE_FILE"

# Reload aliases
source "$PROFILE_FILE"

echo "✅ PDF Tool installed and synced with Potentia Protocol."
echo "📄 Type pdftool to run the PDF conversion tool."
echo "✒️ Edit the drop by typing drops"
