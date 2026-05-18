"""Generate packages/shared-types/index.ts from scaffold_shared_types.schemas."""
from pathlib import Path

from pydantic2ts import generate_typescript_defs

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent.parent
JSON2TS = REPO_ROOT / "node_modules" / ".bin" / "json2ts"
OUT = ROOT / "index.ts"


def main() -> None:
    if not JSON2TS.exists():
        raise SystemExit(
            f"json2ts binary not found at {JSON2TS}. "
            "Run `pnpm add -w -D json-schema-to-typescript` at the repo root first."
        )
    generate_typescript_defs(
        module="scaffold_shared_types.schemas",
        output=str(OUT),
        json2ts_cmd=str(JSON2TS),
    )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
