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
    if mamba env list | grep -q "^CHE_jet"; then
	echo "CHE_jet python environment found"
	cd ./scripts
	echo "▶ Generating figures..."
	for f in scripts/*.py; do
	    # load python env, adapt if needed
	    echo "  ▶ Figure 1: ./scripts/grid_success_rate.py"
	    mamba run -n CHE_jet python grid_success_rate.py
            # echo "  Running $f..."
            # python "$f"
	done
	echo "✓ Figures done."
    else
	echo "CHE_jet python environment not found"
	echo "Please create with mamba env create -f ./scripts/environment.yml"
    fi
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
    echo "✓ Done → manuscript/CHE_GRB_progenitors.pdf"
    if ask "Open manuscript"; then
	xdg-open manuscript/CHE_GRB_progenitors.pdf
    fi
else
    echo "⏭ Skipping manuscript."
fi
