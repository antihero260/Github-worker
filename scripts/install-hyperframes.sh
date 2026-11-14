#!/usr/bin/env bash
# Installe HyperFrames (https://github.com/heygen-com/hyperframes) depuis les sources :
# CLI compilée, skills pour agents IA, Chrome headless de rendu et modules optionnels
# (transcription Parakeet + whisper.cpp, voix Kokoro, musique MusicGen).
#
# Usage : bash scripts/install-hyperframes.sh [--dir CHEMIN] [--minimal] [--no-bashrc]
#
# Le script peut être relancé : il met à jour le clone existant et saute ce qui est déjà en place.
set -euo pipefail

HF_REPO="https://github.com/heygen-com/hyperframes.git"
WHISPER_REPO="https://github.com/ggml-org/whisper.cpp.git"
HF_DIR="${HF_DIR:-$HOME/hyperframes}"
HF_VENV="${HF_VENV:-$HOME/.venvs/hyperframes}"
WHISPER_DIR="$HOME/.cache/hyperframes/whisper/whisper.cpp" # emplacement attendu par la CLI
MINIMAL=0
EDIT_BASHRC=1

usage() {
  cat <<'EOF'
Usage : bash scripts/install-hyperframes.sh [options]

Options :
  --dir CHEMIN   Dossier du clone HyperFrames (défaut : ~/hyperframes, ou $HF_DIR)
  --minimal      Installe seulement la CLI, les skills et Chrome (sans transcription, voix ni musique)
  --no-bashrc    N'ajoute pas HYPERFRAMES_PYTHON dans ~/.bashrc
  -h, --help     Affiche cette aide

Prérequis : git, Node.js 22+, bun, ffmpeg.
Modules optionnels : python3 avec venv (Kokoro, MusicGen), cmake et un compilateur C (whisper.cpp).
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dir) [ $# -ge 2 ] || { echo "--dir attend un chemin" >&2; exit 2; }; HF_DIR="$2"; shift 2 ;;
    --minimal) MINIMAL=1; shift ;;
    --no-bashrc) EDIT_BASHRC=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Option inconnue : $1" >&2; usage >&2; exit 2 ;;
  esac
done

step() { printf '\n==> %s\n' "$*"; }
warn() { printf 'ATTENTION : %s\n' "$*" >&2; }
die() { printf 'ERREUR : %s\n' "$*" >&2; exit 1; }
has() { command -v "$1" >/dev/null 2>&1; }

# --- Prérequis ---------------------------------------------------------------
step "Vérification des prérequis"
for tool in git node bun ffmpeg ffprobe; do
  has "$tool" || die "$tool est introuvable. Installez-le puis relancez le script."
done
node_major="$(node -p 'process.versions.node.split(".")[0]')"
[ "$node_major" -ge 22 ] || die "Node.js 22 ou plus est requis (version trouvée : $(node --version))."
echo "node $(node --version), bun $(bun --version), $(ffmpeg -version | head -n 1 | cut -d' ' -f1-3)"

# --- Code source ---------------------------------------------------------------
if [ -d "$HF_DIR/.git" ]; then
  step "Mise à jour du clone existant : $HF_DIR"
  # bun install réécrit les versions de bun.lock : on remet le fichier d'origine avant de tirer.
  git -C "$HF_DIR" checkout -- bun.lock 2>/dev/null || true
  git -C "$HF_DIR" pull --ff-only || warn "mise à jour impossible (modifications locales ?), on garde la version actuelle."
elif [ -e "$HF_DIR" ]; then
  die "$HF_DIR existe déjà mais n'est pas un clone git. Choisissez un autre dossier avec --dir."
else
  step "Clonage de HyperFrames dans $HF_DIR"
  git clone "$HF_REPO" "$HF_DIR"
fi

step "Installation des dépendances (bun install)"
(cd "$HF_DIR" && bun install)

step "Compilation de tous les paquets (bun run build)"
(cd "$HF_DIR" && bun run build)

# --- Commande hyperframes ------------------------------------------------------
step "Installation de la commande hyperframes"
CLI_BIN="$HF_DIR/packages/cli/bin"
chmod +x "$CLI_BIN"/*.mjs
if [ -w /usr/local/bin ]; then
  BIN_DIR=/usr/local/bin
else
  BIN_DIR="$HOME/.local/bin"
  mkdir -p "$BIN_DIR"
fi
ln -sf "$CLI_BIN/hyperframes.mjs" "$BIN_DIR/hyperframes"
ln -sf "$CLI_BIN/hyperframes-localize-fonts.mjs" "$BIN_DIR/hyperframes-localize-fonts"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) warn "$BIN_DIR n'est pas dans le PATH ; ajoutez-le pour utiliser hyperframes directement."; export PATH="$BIN_DIR:$PATH" ;;
esac
echo "hyperframes $(hyperframes --version) -> $BIN_DIR/hyperframes"

# --- Skills et navigateur ------------------------------------------------------
step "Installation de tous les skills HyperFrames pour les agents IA"
hyperframes skills

step "Téléchargement du Chrome headless de rendu"
hyperframes browser ensure

# --- Modules optionnels ---------------------------------------------------------
if [ "$MINIMAL" -eq 0 ]; then
  step "Modèle de transcription Parakeet"
  hyperframes models install parakeet || warn "installation de Parakeet échouée."

  step "whisper.cpp (transcription)"
  if [ -x "$WHISPER_DIR/build/bin/whisper-cli" ]; then
    echo "déjà compilé : $WHISPER_DIR/build/bin/whisper-cli"
  elif has cmake && { has cc || has gcc || has clang; }; then
    rm -rf "$WHISPER_DIR"
    mkdir -p "$(dirname "$WHISPER_DIR")"
    if git clone --depth 1 "$WHISPER_REPO" "$WHISPER_DIR" &&
      cmake -S "$WHISPER_DIR" -B "$WHISPER_DIR/build" -DCMAKE_BUILD_TYPE=Release &&
      cmake --build "$WHISPER_DIR/build" --config Release -j "$(nproc 2>/dev/null || echo 2)"; then
      echo "compilé : $WHISPER_DIR/build/bin/whisper-cli"
    else
      warn "compilation de whisper.cpp échouée."
    fi
  else
    warn "cmake ou compilateur C absent : whisper.cpp ignoré."
  fi

  step "Environnement Python pour Kokoro (voix) et MusicGen (musique) : $HF_VENV"
  if ! has python3; then
    warn "python3 absent : Kokoro et MusicGen ignorés."
  elif ! { [ -x "$HF_VENV/bin/python" ] || python3 -m venv "$HF_VENV"; }; then
    warn "création du venv impossible (sur Debian/Ubuntu : apt install python3-venv). Kokoro et MusicGen ignorés."
  else
    "$HF_VENV/bin/pip" install --upgrade pip
    # PyTorch en version CPU : bien plus léger que la version CUDA par défaut.
    "$HF_VENV/bin/pip" install --index-url https://download.pytorch.org/whl/cpu torch
    "$HF_VENV/bin/pip" install kokoro-onnx soundfile transformers numpy
    export HYPERFRAMES_PYTHON="$HF_VENV/bin/python"

    if [ "$EDIT_BASHRC" -eq 1 ]; then
      if grep -q 'HYPERFRAMES_PYTHON=' "$HOME/.bashrc" 2>/dev/null; then
        echo "HYPERFRAMES_PYTHON déjà présent dans ~/.bashrc"
      else
        printf '\n# HyperFrames : Python avec Kokoro (voix) et MusicGen (musique)\nexport HYPERFRAMES_PYTHON="%s"\n' \
          "$HYPERFRAMES_PYTHON" >>"$HOME/.bashrc"
        echo "HYPERFRAMES_PYTHON ajouté à ~/.bashrc"
      fi
    else
      echo "Pensez à exporter HYPERFRAMES_PYTHON=\"$HYPERFRAMES_PYTHON\" avant d'utiliser Kokoro ou MusicGen."
    fi
  fi
fi

# --- Bilan ------------------------------------------------------------------------
step "Diagnostic final (hyperframes doctor)"
hyperframes doctor || warn "certains contrôles ont échoué : voir les indications ci-dessus (Docker est facultatif)."
if [ "$MINIMAL" -eq 1 ]; then
  echo "Mode --minimal : les lignes ✗ sur whisper-cpp, Kokoro et MusicGen sont normales (modules non installés)."
fi

printf '\nHyperFrames est installé. Essai rapide :\n  hyperframes init ma-video && cd ma-video && hyperframes render -o ma-video.mp4\n'
