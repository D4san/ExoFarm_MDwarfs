#!/usr/bin/env bash
set -euo pipefail

LPJML_TAG="v6.0.6"
LPJML_COMMIT="5af44a1ed023279a23c28d6dfe76945b97aaac57"
RUNTIME_ROOT="${HOME}/exofarm-lpjml-runtime"
INSTALL_DEPS=0

usage() {
  cat <<'MSG'
Usage: setup_lpjml_mpi.sh [options]

Install and validate the pinned LPJmL MPI build on the execution PC.

Options:
  --runtime-root PATH  Linux-filesystem runtime root.
  --install-deps      Install Ubuntu packages with sudo apt-get.
  -h, --help          Show this help.

The script never replaces an existing source directory. LPJmL is pinned to
v6.0.6, commit 5af44a1ed023279a23c28d6dfe76945b97aaac57.
MSG
}

while (($#)); do
  case "$1" in
    --runtime-root)
      RUNTIME_ROOT="$2"
      shift 2
      ;;
    --install-deps)
      INSTALL_DEPS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This setup must run inside Ubuntu/Linux, not PowerShell." >&2
  exit 3
fi
if [[ "$RUNTIME_ROOT" == /mnt/* ]]; then
  echo "Use the Linux filesystem for runtime and compilation, not /mnt/*: $RUNTIME_ROOT" >&2
  exit 3
fi

if [[ "$INSTALL_DEPS" -eq 1 ]]; then
  sudo apt-get update
  sudo apt-get install -y \
    build-essential ca-certificates git curl \
    libjson-c-dev libnetcdf-dev libudunits2-dev zlib1g-dev \
    mpich libmpich-dev \
    python3 python3-numpy python3-scipy
fi

required_commands=(git make gcc mpicc mpirun python3)
for command_name in "${required_commands[@]}"; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing command: $command_name" >&2
    echo "Re-run with --install-deps on Ubuntu or install the equivalent packages." >&2
    exit 4
  fi
done

mkdir -p "$RUNTIME_ROOT"
LPJML_ROOT="$RUNTIME_ROOT/LPJmL-6.0.6"
if [[ ! -e "$LPJML_ROOT" ]]; then
  git clone --branch "$LPJML_TAG" --depth 1 \
    https://github.com/PIK-LPJmL/LPJmL.git "$LPJML_ROOT"
elif [[ ! -d "$LPJML_ROOT/.git" ]]; then
  echo "Existing path is not an LPJmL Git checkout: $LPJML_ROOT" >&2
  exit 5
fi

ACTUAL_COMMIT="$(git -C "$LPJML_ROOT" rev-parse HEAD)"
if [[ "$ACTUAL_COMMIT" != "$LPJML_COMMIT" ]]; then
  echo "Unexpected LPJmL commit: $ACTUAL_COMMIT" >&2
  echo "Expected: $LPJML_COMMIT" >&2
  echo "The script will not modify or replace this checkout." >&2
  exit 6
fi

cd "$LPJML_ROOT"
./configure.sh -noerror
if ! grep -q -- '-DUSE_MPI' Makefile.inc || ! grep -Eq '^CC[[:space:]]*=[[:space:]]*mpicc' Makefile.inc; then
  echo "configure.sh did not select the MPI build." >&2
  exit 7
fi

# LPJmL 6.0.6 is built serially even though the resulting executable uses MPI;
# this avoids known parallel-build races in generated dependencies.
make clean
make -j1 main
make -j1 utils
make test

if [[ ! -x bin/lpjml || ! -x bin/lpjcheck ]]; then
  echo "LPJmL executables were not produced." >&2
  exit 8
fi

MANIFEST="$RUNTIME_ROOT/lpjml_mpi_installation.txt"
{
  printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'lpjml_root=%s\n' "$LPJML_ROOT"
  printf 'lpjml_tag=%s\n' "$LPJML_TAG"
  printf 'lpjml_commit=%s\n' "$ACTUAL_COMMIT"
  printf 'mpicc=%s\n' "$(command -v mpicc)"
  printf 'mpirun=%s\n' "$(command -v mpirun)"
  printf 'logical_cpus=%s\n' "$(nproc)"
  grep -E '^(CC|CFLAGS|CPPFLAGS)[[:space:]]*=' Makefile.inc || true
} >"$MANIFEST"

printf '%s\n' "$LPJML_ROOT"
printf 'Installation manifest: %s\n' "$MANIFEST"

