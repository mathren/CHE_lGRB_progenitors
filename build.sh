#!/bin/bash
set -e

# --- Helpers ---
ask() {
    read -r -p "$1 [y/N] " answer
    [[ "$answer" =~ ^[Yy]$ ]]
}

# --- Download data ---
if ask "Download data?" ; then
    echo "▶ Downloading data with helper script"
    bash ./scripts/data_prep.sh || echo "Data preparation failed"
else
    echo "⏭ Skipping downloading data/"
    echo "You can manually download the data and unpack them in ./data"
    echo "Assume ./data is populated from now on"
fi

# --- Figures ---
if ask "Generate figures?"; then
    echo "▶ Generating figures..."
    for f in scripts/*.py; do
	# load python env, adapt if needed
	mamba activate CHE_jet
	echo "I should be making figs"
        # echo "  Running $f..."
        # python "$f"
    done
    echo "✓ Figures done."
else
    echo "⏭ Skipping figures."
fi

# --- LaTeX ---
if ask "Build manuscript?"; then
    echo "▶ Building manuscript..."
    cd manuscript
    # adapt to your Latex configuration if needed
    pdflatex CHE_GRB_progenitors.tex
    bibtex CHE_GRB_progenitors
    pdflatex CHE_GRB_progenitors.tex
    pdflatex CHE_GRB_progenitors.tex
    cd ..
    echo "✓ Done → manuscript/main.pdf"
else
    echo "⏭ Skipping manuscript."
fi
