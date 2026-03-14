# Metaverse 32 Bundle

1. Edit `genesis-32-layer-manifest.yaml` if you want to change timestamps, coordinates, or policy.
2. Run:

```bash
python3 create-genesis-32-aztec.py
```

3. Use the printed manifest hash and seed.
4. Encode `genesis-32-layer-manifest.yaml` as an Aztec payload using your preferred encoder.

This bundle does not include an Aztec image generator. It freezes the manifest and deterministic seed derivation step.
