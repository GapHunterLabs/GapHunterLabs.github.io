from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
BEFORE = ROOT / "_review" / "screenshots" / "before"
AFTER = ROOT / "_review" / "screenshots" / "after"


def diff(name: str) -> None:
    a = Image.open(BEFORE / name).convert("RGB")
    b = Image.open(AFTER / name).convert("RGB")
    if a.size != b.size:
        print(f"{name}: size {a.size} -> {b.size}")
        return
    delta = ImageChops.difference(a, b)
    extrema = delta.getextrema()
    changed = sum(1 for px in delta.getdata() if px != (0, 0, 0))
    total = a.size[0] * a.size[1]
    max_delta = max(ch[1] for ch in extrema)
    print(f"{name}: {changed}/{total} px ({100*changed/total:.3f}%) max-channel={max_delta}")


if __name__ == "__main__":
    for path in sorted(BEFORE.glob("*.png")):
        diff(path.name)
