from __future__ import annotations
import argparse
from .utils import ensure_dir, save_json

def main():
    p = argparse.ArgumentParser(prog="fab-aware-codesign")
    p.add_argument("--outdir", type=str, default="outputs/runs/smoke")
    args = p.parse_args()

    out = ensure_dir(args.outdir)
    save_json({"status": "ok", "outdir": str(out)}, out / "smoke.json")
    print(f"Wrote: {out / 'smoke.json'}")

if __name__ == "__main__":
    main()
