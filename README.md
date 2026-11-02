# Air-Gapped d8 Dice to BIP39 Seed Generator

A secure, offline-first command-line tool that converts raw 8-sided dice (`d8`) rolls into a cryptographically valid BIP39 seed phrase (12 or 24 words), complete with SHA-256 checksum verification, optional secure JSON export, and terminal QR code rendering.

---

## Hardware & Preparation Requirements

* **8-sided dice (d8):** You will need **5 to 10 d8 dice** to make rolling efficient (though a single d8 rolled repeatedly will also work).
  * For a **12-word seed**, you need **43 rolls** total.
  * For a **24-word seed**, you need **86 rolls** total.
* **Official BIP39 Wordlist (`english.txt`):** You must provide the official 2,048-word lexicon in the root project directory.

### Downloading & Verifying the Wordlist
1. Use the file provided in this repository.
2. **Download:** Grab the raw official file from the Bitcoin BIP39 GitHub repository:
   * [Download english.txt](https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt)
   * *Via terminal (while online):*
     ```bash
     curl -O [https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt](https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt)
     ```
3. **Verify Line Count:** The file must contain exactly 2,048 lines (one word per line). Run this command to verify:
   ```bash
   wc -l english.txt
   ```
   Expected output: `2048 english.txt` (If the count is anything other than 2048, the file is corrupted or incorrect).

## Environment Preparation & Installation via `uv`

This project uses **`uv`**, an extremely fast Python package installer and virtual environment manager.

### Step 1: Install `uv` (If Not Already Installed)
If you don't have `uv` on your machine, install it via the official standalone installer:
* **macOS / Linux:**
  ```bash
  curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
* **Windows (PowerShell):**
  ```powershell
  powershell -c "irm [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | iex"
  ```

### Step 2: Set Up the Local Environment
Navigate to your project directory in the terminal and initialize a local virtual environment with uv:
  ```bash
  uv venv
  ```

### Step 3: Install Dependencies
Install the required packages (qrcode with Pillow support) using `uv pip`:
  ```bash
  uv pip install -r requirements.txt
  ```

## How to Run the Tool
You can run the script using either your activated virtual environment or uv run for streamlined execution.

### Option A: Standard Execution (Using Activated Environment)
Activate the environment:
  ```bash
  source .venv/bin/activate  # On Windows: `.venv\Scripts\activate`
  ```

Run the script with your d8 rolls:
  ```bash
  python3 d8_bip39.py -w 12 -r "3728154628317542681375246813572461835724618"
  ```

### Option B: Streamlined Execution via `uv run`
Execute the script directly through uv without manually managing virtual environment shells:
  ```bash
  uv run python d8_bip39.py -w 12 -r "3728154628317542681375246813572461835724618"
  ```

## Command-Line Arguments & Flags
| Flag | Argument | Description |
| :--- | :--- | :--- |
| `-w`, `--words` | `12` or `24` | Target seed word count (default: 12). |
| `-r`, `--rolls` | String (1–8) | Continuous string of d8 dice rolls (43 chars for 12 words, 86 for 24 words). |
| `-o`, `--output` | File path | Save seed and metadata to a JSON file (automatically sets restricted `0600` permissions). |
| `-q`, `--qrcode` | *None* | Render the generated seed phrase as an ASCII scannable QR code directly in the terminal. |

Example Combining Backup Export and Terminal QR Code:
  ```bash
  uv run python d8_bip39.py -w 12 -r "3728154628317542681375246813572461835724618" -o wallet_backup.json -q
  ```

## Project Directory Structure
```text
d8-seed-generator/
├── d8_bip39.py        # Main Python script
├── english.txt        # Official BIP39 wordlist (2048 words)
├── requirements.txt   # Python dependencies
├── .gitignore         # Git exclusion rules
├── README.md          # Documentation
└── LICENSE            # UnLicense
```
