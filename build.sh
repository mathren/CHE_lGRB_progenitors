#!/bin/bash
set -e

# --- Usage ---
usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Interactively reproduce the paper: download data, build the python
environment with mamba, generate figures, and compile the manuscript.

Options:
  -y,  --yes          Answer yes to all prompts (non-interactive)
  -nd, --no-download  Skip downloading data
       --create-env   Create mamba env (skipped by default)
  -nf, --no-figures   Skip generating figures
  -nt, --no-latex     Skip building the manuscript
  -h,  --help         Show this help message and exit

Examples:
  $(basename "$0")                        # fully interactive
  $(basename "$0") --yes                  # auto-accept all steps
  $(basename "$0") --yes --no-download    # skip download, auto-accept rest
  $(basename "$0") --yes --create-env     # auto-accept all steps, build env
EOF
}

# --- Parse arguments ---
YES_ALL=false
NO_DOWNLOAD=false
BUILD_ENV=false
NO_FIGURES=false
NO_LATEX=false
# Loop over command line arguments
# --yes or -y result in auto-answering yes to all the prompts
for arg in "$@"; do
    case "$arg" in
        --yes|-y)          YES_ALL=true ;;
	--no-download|-nd) NO_DOWNLOAD=true ;;
	--create-env)      BUILD_ENV=true ;;
	--no-figures|-nf)  NO_FIGURES=true ;;
	--no-latex|-nt)    NO_LATEX=true ;;
	--help|-h)         usage; exit 0 ;;
    esac
done

# --- Helpers ---
ask() {
    if $YES_ALL; then
        echo "$1 [y/N] y (auto)"
        return 0
    fi
    read -r -p "$1 [y/N] " answer
    [[ "$answer" =~ ^[Yy]$ ]]
}

# --- Download data ---
if ! $NO_DOWNLOAD && ask "Download data?" ; then
    echo "▶ Downloading data with helper script"
    bash ./scripts/data_prep.sh || echo "✘ Data preparation failed"
else
    echo "⏭ Skipping downloading data/"
    echo "You can manually download the data and unpack them in ./data"
    echo "Continue assuming ./data is populated from now on"
fi

# --- Create the python environment ---
if  $BUILD_ENV && ask "Create python environment?" ; then
    echo "▶ Generating CHE_jet python environment ..."
    cd ./scripts/
    mamba create -f environment.yml
    echo "✓ python environment created."
    cd ..
else
    echo "⏭ Skipping creating environment"
    echo "Continue assuming CHE_jet environment exists and mamba is available"
fi

# --- Figures ---
if ! $NO_FIGURES && ask "Generate figures?"; then
    if mamba env list | grep -q "^CHE_jet"; then
	echo "✓ CHE_jet python environment found"
	cd ./scripts
	echo "▶ Generating figures..."
	echo "  ▶ Figure 1: ./scripts/grid_success_rate.py"
	mamba run -n CHE_jet python grid_success_rate.py
	echo "  ▶ Figure 2: ./scripts/multi_panel.py"
	mamba run -n CHE_jet python multi_panel.py
	echo "  ▶ Figure 3: ./scripts/entropy.py"
	mamba run -n CHE_jet python entropy.py
	echo "  ▶ Figure 4: ./scripts/B-fields.py"
	mamba run -n CHE_jet python B-fields.py
	echo "  ▶ Figure 5: ./scripts/xi_M.py"
	mamba run -n CHE_jet python xi_M.py
	cd ..
	echo "✓ Figures done."
    else
	echo "✘ python environment CHE_jet not found"
	echo "Please create with mamba env create -f ./scripts/environment.yml"
    fi
else
    echo "⏭ Skipping figures."
    echo "Continue assuming the figures are in ./manuscript/figures/"
fi

# --- LaTeX ---
if ! $NO_LATEX && ask "Build manuscript?"; then
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
	xdg-open manuscript/CHE_GRB_progenitors.pdf &
    fi
else
    echo "⏭ Skipping building manuscript."
fi
