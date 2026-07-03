from __future__ import annotations

import argparse
import gzip
import shutil
import pathlib
import posixpath
import socket
import tarfile
import time
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parent
CLEAN_SOURCE_DIR = "source_clean"
socket.setdefaulttimeout(240)

ARXIV_IDS = {
    "Dreamer": "1912.01603",
    "DreamerV2": "2010.02193",
    "DreamerV3": "2301.04104",
    "DreamerV4": "2509.24527",
    "DriveDreamer": "2309.09777",
    "GAIA": "2311.12983",
    "Genie": "2402.15391",
    "MuZero": "1911.08265",
    "PlaNet": "1811.04551",
    "TD-MPC": "2203.04955",
    "WorldModel": "1803.10122",
}


def is_valid_tar(path: pathlib.Path) -> bool:
    if not path.exists() or path.stat().st_size < 1024:
        return False
    try:
        with tarfile.open(path, "r:*") as tf:
            tf.getmembers()
        return True
    except (tarfile.TarError, EOFError):
        return False


def safe_member_path(target_dir: pathlib.Path, member_name: str) -> pathlib.Path:
    target_root = target_dir.resolve()
    normalized = posixpath.normpath(member_name)
    if normalized.startswith("../") or normalized == ".." or posixpath.isabs(normalized):
        raise RuntimeError(f"Refusing unsafe tar member path: {member_name}")
    member_path = (target_dir / pathlib.PurePosixPath(normalized)).resolve()
    if target_root not in (member_path, *member_path.parents):
        raise RuntimeError(f"Refusing unsafe tar member path: {member_name}")
    return member_path


def safe_extract_tar(archive: pathlib.Path, target_dir: pathlib.Path) -> None:
    with tarfile.open(archive, "r:*") as tf:
        for member in tf.getmembers():
            member_path = safe_member_path(target_dir, member.name)
            if member.isdir():
                member_path.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                member_path.parent.mkdir(parents=True, exist_ok=True)
                source = tf.extractfile(member)
                if source is None:
                    continue
                with source, member_path.open("wb") as output:
                    shutil.copyfileobj(source, output)
            else:
                print(f"SKIP SPECIAL {member.name}", flush=True)


def extract_source_payload(name: str, archive: pathlib.Path, target_dir: pathlib.Path) -> None:
    try:
        safe_extract_tar(archive, target_dir)
        return
    except (tarfile.TarError, EOFError):
        pass

    try:
        with gzip.open(archive, "rb") as source:
            data = source.read()
        target = target_dir / f"{name}_source.tex"
        target.write_bytes(data)
        print(f"EXTRACTED GZIP TEX {name}: {target.name}", flush=True)
        return
    except OSError:
        target = target_dir / f"{name}_source_payload"
        shutil.copy2(archive, target)
        print(f"COPIED NON-TAR {name}: {target.name}", flush=True)


def selected_papers(args: argparse.Namespace) -> list[tuple[str, str]]:
    selected = ARXIV_IDS
    if args.paper:
        wanted = set(args.paper)
        missing = sorted(wanted - set(ARXIV_IDS))
        if missing:
            raise SystemExit(f"Unknown paper name(s): {', '.join(missing)}")
        selected = {name: ARXIV_IDS[name] for name in args.paper}
    skipped = set(args.skip or [])
    return [(name, arxiv_id) for name, arxiv_id in selected.items() if name not in skipped]


def download_archive(name: str, arxiv_id: str, archive: pathlib.Path) -> None:
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    temp_archive = archive.with_name(f"{name}_arxiv_source.tmp")
    if temp_archive.exists():
        temp_archive.unlink()
    print(f"DOWNLOAD {name} {arxiv_id}", flush=True)
    with temp_archive.open("wb") as file, urllib.request.urlopen(url) as response:
        shutil.copyfileobj(response, file)
    temp_archive.replace(archive)
    time.sleep(1)


def process_paper(name: str, arxiv_id: str, force: bool = False) -> None:
    paper_dir = ROOT / name
    source_dir = paper_dir / CLEAN_SOURCE_DIR
    source_dir.mkdir(exist_ok=True)
    archive = paper_dir / "source.tar.gz"

    if any(source_dir.iterdir()) and not force:
        print(f"SKIP {name}: source not empty", flush=True)
        return

    if force and any(source_dir.iterdir()):
        if paper_dir.resolve() not in (source_dir.resolve(), *source_dir.resolve().parents):
            raise RuntimeError(f"Refusing to remove unexpected path: {source_dir}")
        print(f"REFRESH {name}: removing generated clean source files", flush=True)
        shutil.rmtree(source_dir)
        source_dir.mkdir(exist_ok=True)

    if not is_valid_tar(archive):
        if archive.exists() and archive.stat().st_size >= 1024:
            print(f"INVALID ARCHIVE {name}: replacing {archive.name}", flush=True)
        download_archive(name, arxiv_id, archive)

    try:
        extract_source_payload(name, archive, source_dir)
        entry_count = sum(1 for _ in source_dir.rglob("*"))
        tex_count = sum(1 for _ in source_dir.rglob("*.tex"))
        print(f"READY {name}: {entry_count} entries, {tex_count} tex files in {CLEAN_SOURCE_DIR}", flush=True)
    except (tarfile.TarError, RuntimeError, EOFError):
        if archive.exists():
            archive.unlink()
        print(f"RETRY {name}: archive was not a safe tar source", flush=True)
        download_archive(name, arxiv_id, archive)
        extract_source_payload(name, archive, source_dir)
        entry_count = sum(1 for _ in source_dir.rglob("*"))
        tex_count = sum(1 for _ in source_dir.rglob("*.tex"))
        print(f"READY {name}: {entry_count} entries, {tex_count} tex files in {CLEAN_SOURCE_DIR}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and extract arXiv paper sources.")
    parser.add_argument("--paper", action="append", help="Only process this paper name. May be repeated.")
    parser.add_argument(
        "--skip",
        action="append",
        default=["DreamerV3"],
        help="Skip this paper name. May be repeated. Defaults to DreamerV3.",
    )
    parser.add_argument("--force", action="store_true", help=f"Re-extract a paper even when {CLEAN_SOURCE_DIR}/ is non-empty.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    failures = []
    for name, arxiv_id in selected_papers(args):
        try:
            process_paper(name, arxiv_id, force=args.force)
        except Exception as exc:  # Keep later papers moving; print enough context for follow-up.
            failures.append(name)
            print(f"ERROR {name}: {type(exc).__name__}: {exc}", flush=True)
    if failures:
        raise SystemExit(f"Failed papers: {', '.join(failures)}")


if __name__ == "__main__":
    main()
