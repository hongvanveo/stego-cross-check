#!/usr/bin/env python3
import argparse
import hashlib
import math
import os
import random
import wave
from array import array
from pathlib import Path


FRAME_LEN = 1024
LSB_MAGIC = b"LSBX"
LSB_REPETITIONS = 64
DWT_MAGIC = "DWTCROSS"


def mark(token):
    result = os.path.expanduser("~/.local/result/cross_check_status.txt")
    os.makedirs(os.path.dirname(result), exist_ok=True)
    existing = ""
    if os.path.exists(result):
        with open(result, "r", encoding="utf-8") as handle:
            existing = handle.read()
    if token not in existing:
        with open(result, "a", encoding="utf-8") as handle:
            handle.write(token + "\n")


def write_marker(name):
    Path(name).write_text("done\n", encoding="utf-8")


def bits_to_bytes(bits):
    out = bytearray()
    for start in range(0, len(bits), 8):
        byte = 0
        for bit in bits[start:start + 8]:
            byte = (byte << 1) | bit
        out.append(byte)
    return bytes(out)


def get_lsb(sample):
    raw = sample if sample >= 0 else sample + 65536
    return raw & 1


def read_repeated_bits(samples, bit_count):
    bits = []
    for bit_index in range(bit_count):
        start = bit_index * LSB_REPETITIONS
        chunk = samples[start:start + LSB_REPETITIONS]
        ones = sum(get_lsb(value) for value in chunk)
        bits.append(1 if ones >= (len(chunk) / 2.0) else 0)
    return bits


def extract_lsb_message(samples):
    prefix_bits = read_repeated_bits(samples, (len(LSB_MAGIC) + 1) * 8)
    prefix = bits_to_bytes(prefix_bits)
    if len(prefix) < 5 or prefix[:4] != LSB_MAGIC:
        return False, None, False
    message_length = prefix[4]
    total_bytes = 4 + 1 + message_length + 4
    total_bits = total_bytes * 8
    payload = bits_to_bytes(read_repeated_bits(samples, total_bits))
    if payload[:4] != LSB_MAGIC:
        return False, None, False
    body = payload[5:5 + message_length]
    expected = payload[5 + message_length:5 + message_length + 4]
    actual = hashlib.sha256(body).digest()[:4]
    return True, body, expected == actual


def dwt_bits(message_bytes):
    digest = hashlib.sha256(message_bytes).digest()
    raw = digest[:6]
    bits = []
    for byte in raw:
        for shift in range(7, -1, -1):
            bits.append(1 if (byte >> shift) & 1 else -1)
    return bits


def pn_sequence(key, bit_index, length):
    seed = int(
        hashlib.sha256(f"{DWT_MAGIC}:{key}:{bit_index}".encode("utf-8")).hexdigest()[:16],
        16,
    )
    rng = random.Random(seed)
    return [1.0 if rng.random() >= 0.5 else -1.0 for _ in range(length)]


def read_wav(path):
    with wave.open(path, "rb") as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError("chi ho tro WAV mono PCM16")
        samples = array("h")
        samples.frombytes(wav.readframes(wav.getnframes()))
    return list(samples)


def norm(values):
    return math.sqrt(sum(value * value for value in values)) + 1e-12


def dwt_score(samples, message_bytes, key):
    bits = dwt_bits(message_bytes)
    frame_count = len(samples) // FRAME_LEN
    if frame_count <= len(bits):
        return 0.0
    scores = [[] for _ in bits]
    for frame_index in range(frame_count):
        start = frame_index * FRAME_LEN
        frame = [float(value) for value in samples[start:start + FRAME_LEN]]
        bit_index = frame_index % len(bits)
        sign = bits[bit_index]
        pn = pn_sequence(key, bit_index, FRAME_LEN)
        score = sum(frame[i] * pn[i] for i in range(FRAME_LEN)) / (norm(frame) * norm(pn))
        scores[bit_index].append(score * sign)
    combined = [sum(bucket) / len(bucket) for bucket in scores if bucket]
    if not combined:
        return 0.0
    return sum(combined) / len(combined)


def classify_dwt(score):
    if score >= 0.17:
        return "FOUND"
    if score >= 0.10:
        return "WEAK"
    return "NOT FOUND"


def mark_progress(path, overall_status):
    name = Path(path).name.lower()
    if name == "marked_cross.wav" and overall_status == "VALID":
        write_marker(".valid_checked_done")
        mark("PASS_VALID_CHECKED")
    if name == "light_modified.wav" and overall_status == "POSSIBLY MODIFIED":
        write_marker(".modified_checked_done")
        mark("PASS_MODIFIED_CHECKED")
    if name == "destroyed.wav" and overall_status == "INVALID OR DESTROYED":
        write_marker(".invalid_checked_done")
        mark("PASS_INVALID_CHECKED")


def main():
    parser = argparse.ArgumentParser(description="Verify hybrid LSB + DWT cross-check markers.")
    parser.add_argument("input")
    parser.add_argument("--key", default=13579, type=int)
    args = parser.parse_args()

    samples = read_wav(args.input)
    lsb_found, message_bytes, integrity_ok = extract_lsb_message(samples)

    if lsb_found and integrity_ok and message_bytes is not None:
        score = dwt_score(samples, message_bytes, args.key)
        dwt_status = classify_dwt(score)
    else:
        score = 0.0
        dwt_status = "NOT FOUND"

    lsb_status = "FOUND" if lsb_found else "NOT FOUND"
    integrity_status = "OK" if lsb_found and integrity_ok else "FAIL"

    if lsb_status == "FOUND" and integrity_status == "OK" and dwt_status == "FOUND":
        overall_status = "VALID"
    elif lsb_status == "FOUND" and integrity_status == "OK" and dwt_status == "WEAK":
        overall_status = "POSSIBLY MODIFIED"
    else:
        overall_status = "INVALID OR DESTROYED"

    mark_progress(args.input, overall_status)

    print(f"File: {Path(args.input).name}")
    print(f"LSB marker: {lsb_status}")
    print(f"DWT marker: {dwt_status}")
    print(f"Message integrity: {integrity_status}")
    print(f"Overall status: {overall_status}")
    print(f"DWT score: {score:.3f}")
    if message_bytes is not None and lsb_found:
        print(f"Message: {message_bytes.decode('utf-8', errors='replace')}")


if __name__ == "__main__":
    main()
