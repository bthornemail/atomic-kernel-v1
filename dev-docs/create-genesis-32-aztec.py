#!/usr/bin/env python3
import hashlib
from pathlib import Path

MASK = (1 << 256) - 1
C_256 = int("1D" * 16, 16)

def rotl(x: int, n: int, width: int = 256) -> int:
    return ((x << n) | (x >> (width - n))) & ((1 << width) - 1)

def rotr(x: int, n: int, width: int = 256) -> int:
    return ((x >> n) | (x << (width - n))) & ((1 << width) - 1)

def oscillate(x: int) -> int:
    return (rotl(x, 1) ^ rotl(x, 3) ^ rotr(x, 2) ^ C_256) & MASK

def derive_genesis_seed(yaml_bytes: bytes) -> int:
    context_hash = int.from_bytes(hashlib.sha256(yaml_bytes).digest(), "big")
    return oscillate(context_hash & MASK)

def main() -> None:
    manifest_path = Path("genesis-32-layer-manifest.yaml")
    yaml_bytes = manifest_path.read_bytes()
    seed = derive_genesis_seed(yaml_bytes)
    payload_hash = hashlib.sha256(yaml_bytes).hexdigest()
    print(f"manifest_sha256=sha256:{payload_hash}")
    print(f"genesis_seed_256=0x{seed:064x}")
    print("Next: encode genesis-32-layer-manifest.yaml as an Aztec payload with your preferred encoder.")

if __name__ == "__main__":
    main()
