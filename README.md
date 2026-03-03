# ◈ CYBER STEGANOGRAPHY ◈

> **Hide your secrets in plain sight.** A stunning, cyber-themed Least Significant Bit (LSB) image steganography tool built in Python.

https://github.com/sabarishmettu/Image-Steganography/raw/main/STEGANOGRAPHY/Images/STEGANOGRAPHY_Video.mp4

## 🚀 Features

- **Matrix Rain Background:** Animated falling character effect inspired by *The Matrix*.
- **Neon Interface:** Glowing cyan, green, and purple interactive buttons and frames.
- **Hacker Console:** Real-time logging of system events in a classic terminal style.
- **Password Encryption:** Secure your hidden messages using SHA-256 XOR Cipher and Base64 wrapping, complete with hash validation.
- **Capacity Indicator:** Automatically calculates how many characters your selected image can securely hold.
- **Cyber-Themed Alerts:** Custom "Access Denied" and error glitch popups.
- **Smart Image Handling:** Automatically converts indexed (P mode) images like logos to RGB to prevent encoding failures.

## 🛠️ Requirements

The application uses Python 3 and a few external libraries. Ensure you have them installed:

```bash
pip install stegano Pillow
```

## 🎮 How to Use

1. **Launch the application:**
   ```bash
   python steganography.py
   ```
2. **Load Image:** Click `⟦ LOAD IMAGE ⟧` to select the image (PNG, JPG, BMP) you want to use as your cover.
3. **Type Secret Message:** Enter the text you wish to hide in the top-right text area.
4. **Set Password (Optional):** Enter a password in the password field to encrypt your message. 
5. **Encode:** Click `⟦ ENCODE ▶ ⟧` to embed your message into the image.
6. **Save Image:** Click `⟦ SAVE IMAGE ⟧` to export your new, steganographic image file.

**To Decode:**
1. Click `⟦ LOAD IMAGE ⟧` and select your previously saved encoded image.
2. If you used a password, enter it in the password field.
3. Click `⟦ DECODE ◀ ⟧` to reveal your secret message!

## 🧩 How it Works

The app uses **LSB (Least Significant Bit)** steganography. It modifies the last bit of the color values in an image's pixels. Because human eyes cannot distinguish a color difference of a single bit (e.g., RGB `(255, 0, 0)` vs `(254, 0, 0)`), the secret data is visually undetectable.

If a password is used, the message is first encrypted using a fast SHA-256 XOR cipher, wrapped in Base64 (to survive the LSB round-trip), and embedded with a verification hash to ensure wrong passwords are automatically rejected.

## ⚖️ License
Feel free to use and modify the code!
