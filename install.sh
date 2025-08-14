#!/data/data/com.termux/files/usr/bin/bash

echo "🔧 Bootstrapping Potentia PDF Tool Protocol..."
sleep 2

# ✅ Update system & install base packages
pkg update -y
pkg upgrade -y
pkg install python termux-api -y

# ✅ Python dependencies
pip install --upgrade pip
pip install img2pdf Pillow PyMuPDF

# 📁 Potentia base dirs
mkdir -p ~/potentia/drops
mkdir -p ~/potentia/config
mkdir -p ~/potentia/logs

# 📁 Move current folder into pdf_tool drop folder
CURRENT_DIR=$(pwd)
DROP_DEST=~/potentia/drops/pdf_tool
rm -rf "$DROP_DEST"
mkdir -p "$DROP_DEST"
cp -r "$CURRENT_DIR"/* "$DROP_DEST"

# 📜 Ensure logs exist
touch ~/potentia/logs/potentia.log
touch "$DROP_DEST/pdf_tool.log"

# ⚙️ Config file
CONFIG_FILE=~/potentia/config/potentia.env
if [ ! -f "$CONFIG_FILE" ]; then
    echo "# Potentia Config" > "$CONFIG_FILE"
    echo "PDF_TOOL_ENABLED=true" >> "$CONFIG_FILE"
    echo "INSTALL_DATE=$(date)" >> "$CONFIG_FILE"
else
    sed -i "s/PDF_TOOL_ENABLED=.*/PDF_TOOL_ENABLED=true/" "$CONFIG_FILE"
fi

# 🧙 Aliases
SHELL_NAME=$(basename "$SHELL")
if [ "$SHELL_NAME" = "zsh" ]; then
    PROFILE_FILE=~/.zshrc
else
    PROFILE_FILE=~/.bashrc
fi

ALIAS_CMD='alias pdftool="python3 ~/potentia/drops/pdf_tool/pdf_tool.py"'
grep -qxF "$ALIAS_CMD" "$PROFILE_FILE" || echo "$ALIAS_CMD" >> "$PROFILE_FILE"

ALIAS_ENTER='alias drops="cd ~/potentia/drops/pdf_tool/"'
grep -qxF "$ALIAS_ENTER" "$PROFILE_FILE" || echo "$ALIAS_ENTER" >> "$PROFILE_FILE"

# 🔁 Reload shell profile
source "$PROFILE_FILE"

# ⚠️ Storage check
if [ ! -d "/storage/emulated/0" ]; then
    echo "⚠️ Termux storage access is not set up."
    echo "📌 Run this command manually, then allow permission in Android prompt:"
    echo "    termux-setup-storage"
fi

echo "✅ Potentia PDF Tool installed successfully."
echo "📄 Usage: type 'pdftool' to start."
