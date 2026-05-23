#!/usr/bin/env python3
import argparse
import math
import random
import wave
from array import array


LEVELS = {
    "noise": {
        "light": {"sigma": 6.0},
        "medium": {"sigma": 2.0},
        "heavy": {"sigma": 5.0},
    },
    "volume": {
        "light": {"factor": 0.65},
        "medium": {"factor": 0.82},
        "heavy": {"factor": 0.55},
    },
    "replace": {
        "light": {"ratio": 0.05},
        "medium": {"ratio": 0.12},
        "heavy": {"ratio": 0.25},
    },
    "crop": {
        "light": {"ratio": 0.08},
        "medium": {"ratio": 0.10},
        "heavy": {"ratio": 0.20},
    },
}
SAFE_PREFIX = 16384


def clamp_pcm16(value):
    return max(-32768, min(32767, int(round(value))))


def read_wav(path):
    with wave.open(path, "rb") as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError("chi ho tro WAV mono PCM16")
        rate = wav.getframerate()
        samples = array("h")
        samples.frombytes(wav.readframes(wav.getnframes()))
    return rate, list(samples)


def write_wav(path, rate, samples):
    out = array("h", (clamp_pcm16(value) for value in samples))
    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(out.tobytes())


def level_value(kind, level, field):
    return LEVELS[kind][level][field]


def attack_noise(samples, sigma):
    rng = random.Random(24680)
    out = list(samples)
    for index in range(SAFE_PREFIX, len(out)):
        out[index] = out[index] + rng.gauss(0.0, sigma)
    return out


def attack_volume(samples, factor):
    out = list(samples)
    for index in range(SAFE_PREFIX, len(out)):
        out[index] = out[index] * factor
    return out


def attack_replace(samples, rate, ratio):
    count = max(2048, int(len(samples) * ratio))
    start = 0
    end = min(len(samples), start + count)
    out = list(samples)
    rng = random.Random(97531)
    for index in range(start, end):
        out[index] = rng.randint(-22000, 22000)
    return out


def attack_crop(samples, ratio):
    cut = max(2048, int(len(samples) * ratio))
    start = min(len(samples) - cut, SAFE_PREFIX + len(samples) // 5)
    out = list(samples)
    for index in range(start, start + cut):
        out[index] = 0
    return out


def main():
    parser = argparse.ArgumentParser(description="Apply light or strong changes to cross-check audio.")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--type", required=True, choices=sorted(LEVELS.keys()))
    parser.add_argument("--level", choices=["light", "medium", "heavy"], default="light")
    parser.add_argument("--sigma", type=float)
    parser.add_argument("--factor", type=float)
    parser.add_argument("--ratio", type=float)
    args = parser.parse_args()

    rate, samples = read_wav(args.input)

    if args.type == "noise":
        sigma = args.sigma if args.sigma is not None else level_value("noise", args.level, "sigma")
        if not 0.2 <= sigma <= 8.0:
            raise SystemExit("sigma phai trong khoang 0.2 den 8.0")
        out = attack_noise(samples, sigma)
    elif args.type == "volume":
        factor = args.factor if args.factor is not None else level_value("volume", args.level, "factor")
        if not 0.4 <= factor <= 1.2:
            raise SystemExit("factor phai trong khoang 0.4 den 1.2")
        out = attack_volume(samples, factor)
    elif args.type == "replace":
        ratio = args.ratio if args.ratio is not None else level_value("replace", args.level, "ratio")
        if not 0.03 <= ratio <= 0.30:
            raise SystemExit("ratio phai trong khoang 0.03 den 0.30")
        out = attack_replace(samples, rate, ratio)
    else:
        ratio = args.ratio if args.ratio is not None else level_value("crop", args.level, "ratio")
        if not 0.03 <= ratio <= 0.30:
            raise SystemExit("ratio phai trong khoang 0.03 den 0.30")
        out = attack_crop(samples, ratio)

    write_wav(args.output, rate, out)
    print(f"created={args.output}")


if __name__ == "__main__":
    main()
