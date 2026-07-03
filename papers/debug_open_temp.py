from pathlib import Path

path = Path(r"D:\gameWorld\papers\DreamerV4\source.tar.gz.download")
if path.exists():
    path.unlink()
with path.open("wb") as file:
    file.write(b"ok")
print(path, path.stat().st_size)
