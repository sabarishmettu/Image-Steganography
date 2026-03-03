# ◈ CYBER STEGANOGRAPHY ◈

> **"Hide your secrets in plain sight."**
> A stunning, cyber-themed Least Significant Bit (LSB) image steganography tool built in Python.

https://github.com/sabarishmettu/Image-Steganography/blob/main/STEGANOGRAPHY/Images/STEGANOGRAPHY_Video.mp4

---

## 🚀 Features

- 🟢 **Matrix Rain Background:** Animated falling character effect inspired by *The Matrix*.
- 💎 **Neon Interface:** Glowing cyan, green, and purple interactive buttons with hover transitions.
- 🖥️ **Hacker Console:** Real-time logging of system events in a classic terminal output style.
- 🔒 **Password Encryption:** Secure your hidden messages using a fast SHA-256 XOR Cipher wrapped in Base64 (includes built-in hash validation to reject wrong passwords).
- 📊 **Capacity Indicator:** Automatically calculates exactly how many characters your selected image can securely hold.
- ⚠️ **Cyber-Themed Alerts:** Custom "Access Denied" and error glitch popups instead of boring Windows dialogs.
- 🖼️ **Smart Image Handling:** Automatically and silently converts indexed (Mode P) images like logos to RGB to prevent encoding crashes.

---

## 🛠️ Installation & Requirements

The application runs on Python 3 and requires just two libraries. Install them via your terminal:

```bash
pip install stegano Pillow
```

## 🎮 How to Use

### [ ENCODE — Hiding Data ]
1. Run `python steganography.py`
2. Click `⟦ LOAD IMAGE ⟧` and select your cover image (PNG, JPG, BMP).
3. Type the text you wish to hide into the **Secret Message** area.
4. *(Optional)* Enter a password to encrypt your message. 
5. Click `⟦ ENCODE ▶ ⟧` to embed the data into the image pixels.
6. Click `⟦ SAVE IMAGE ⟧` to export your steganographic image file.

### [ DECODE — Revealing Data ]
1. Click `⟦ LOAD IMAGE ⟧` and select your previously saved encoded image.
2. If you used a password during encoding, enter the exact same password.
3. Click `⟦ DECODE ◀ ⟧` — if the password matches, your secret message will be revealed!

---

## 🧩 How it Works (Under the Hood)

This tool utilizes **LSB (Least Significant Bit)** steganography. 
It modifies the very last bit of the RGB color values within an image's pixels. Because the human eye cannot distinguish a color difference of a single bit (for example, RGB `(255, 0, 0)` vs `(254, 0, 0)`), the hidden data is entirely visually undetectable.

To ensure the data survives the delicate LSB read/write process, password-encrypted messages are hashed via SHA-256, XOR-ciphered, and finally wrapped in Base64 encoding.

---

## ⚖️ License
Open source. Feel free to use, modify, and enhance the code!
