#!/usr/bin/env python3
"""
Air-Gapped d8 Dice to BIP39 Seed Generator & Verifier
Converts raw 8-sided dice rolls passed via CLI into a cryptographically valid BIP39 seed phrase,
saves to JSON securely, and optionally displays a terminal QR code.
"""

import argparse
import datetime
import hashlib
import json
import os
import sys

# Optional dependency check for terminal QR code rendering
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# Local wordlist filename expected in the same directory
WORDLIST_FILENAME = "english.txt"

def load_wordlist():
    """Loads the BIP39 English wordlist from a local file for air-gapped execution."""
    if not os.path.exists(WORDLIST_FILENAME):
        raise FileNotFoundError(
            f"'{WORDLIST_FILENAME}' not found in the current directory.\n"
            f"Please save the official BIP39 English wordlist as '{WORDLIST_FILENAME}' alongside this script."
        )

    with open(WORDLIST_FILENAME, 'r', encoding='utf-8') as f:
        words = f.read().splitlines()

    if len(words) != 2048:
        raise ValueError(f"Wordlist '{WORDLIST_FILENAME}' does not contain exactly 2048 words (found {len(words)}).")

    return words

def parse_rolls_string(rolls_str, word_count):
    """
    Cleans and validates the input dice roll string:
    - Strips non-digit characters.
    - Checks for exact length (43 for 12 words, 86 for 24 words).
    - Verifies all digits are within the valid d8 range (1-8).
    """
    cleaned = "".join(c for c in rolls_str if c.isdigit())

    target_entropy_bits = 128 if word_count == 12 else 256
    required_rolls = (target_entropy_bits + 2) // 3

    if len(cleaned) != required_rolls:
        raise ValueError(
            f"Incorrect number of rolls! For a {word_count}-word seed, "
            f"you must provide exactly {required_rolls} rolls. Received {len(cleaned)}."
        )

    rolls = []
    for char in cleaned:
        val = int(char)
        if not (1 <= val <= 8):
            raise ValueError(f"Invalid d8 roll: '{val}'. All rolls must be between 1 and 8.")
        rolls.append(val)

    return rolls

def generate_bip39_seed(rolls, word_count=12):
    """Takes validated d8 rolls, computes checksum, and returns the full BIP39 mnemonic phrase."""
    wordlist = load_wordlist()

    target_entropy_bits = 128 if word_count == 12 else 256
    bit_string = ""
    for roll in rolls:
        bit_string += f"{roll - 1:03b}"

    entropy_bits = bit_string[:target_entropy_bits]
    entropy_bytes = int(entropy_bits, 2).to_bytes(len(entropy_bits) // 8, byteorder='big')

    # Compute SHA-256 checksum
    hash_bytes = hashlib.sha256(entropy_bytes).digest()
    hash_bits = ''.join(f"{b:08b}" for b in hash_bytes)

    checksum_length = word_count // 3
    checksum_bits = hash_bits[:checksum_length]

    full_bits = entropy_bits + checksum_bits

    mnemonic_words = []
    for i in range(0, len(full_bits), 11):
        chunk = full_bits[i:i+11]
        index = int(chunk, 2)
        mnemonic_words.append(wordlist[index])

    return " ".join(mnemonic_words)

def save_to_json(filepath, seed_phrase, word_count, rolls_str):
    """Saves seed data to a JSON file with restricted file permissions (0600)."""
    data = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "word_count": word_count,
        "rolls_provided": rolls_str,
        "seed_phrase": seed_phrase
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    try:
        os.chmod(filepath, 0o600)
    except Exception:
        pass

def print_terminal_qr(text):
    """Renders text as a scannable ASCII QR code in the terminal."""
    if not QR_AVAILABLE:
        print("\n[!] Warning: 'qrcode' package is not installed. Run 'pip install qrcode' to enable terminal QR codes.", file=sys.stderr)
        return

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)

    print("\nScan QR Code:")
    qr.print_ascii(invert=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert d8 dice roll strings into a cryptographically secure BIP39 seed phrase."
    )
    parser.add_argument(
        "-w", "--words",
        type=int,
        choices=[12, 24],
        default=12,
        help="Number of words in the seed phrase (12 or 24). Default is 12."
    )
    parser.add_argument(
        "-r", "--rolls",
        required=True,
        type=str,
        help="Continuous string of d8 rolls (e.g., '3728154628...'). Requires 43 chars for 12 words, 86 for 24 words."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Path to save the output JSON file containing the seed and metadata."
    )
    parser.add_argument(
        "-q", "--qrcode",
        action="store_true",
        help="Render the generated seed phrase as an ASCII QR code in the terminal."
    )

    args = parser.parse_args()

    try:
        validated_rolls = parse_rolls_string(args.rolls, args.words)
        print(f"Successfully validated {len(validated_rolls)} rolls for a {args.words}-word seed.")

        seed_phrase = generate_bip39_seed(validated_rolls, word_count=args.words)
        print("\nGenerated BIP39 Seed Phrase:")
        print(seed_phrase)

        if args.output:
            save_to_json(args.output, seed_phrase, args.words, args.rolls)
            print(f"\n[+] Seed and metadata successfully saved to: {args.output} (Permissions set to 600)")

        if args.qrcode:
            print_terminal_qr(seed_phrase)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
