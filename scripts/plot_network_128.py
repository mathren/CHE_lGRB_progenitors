import re
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt


ELEMENT_Z = {
    "neut": 0,
    "h": 1,
    "he": 2,
    "li": 3,
    "be": 4,
    "b": 5,
    "c": 6,
    "n": 7,
    "o": 8,
    "f": 9,
    "ne": 10,
    "na": 11,
    "mg": 12,
    "al": 13,
    "si": 14,
    "p": 15,
    "s": 16,
    "cl": 17,
    "ar": 18,
    "k": 19,
    "ca": 20,
    "sc": 21,
    "ti": 22,
    "v": 23,
    "cr": 24,
    "mn": 25,
    "fe": 26,
    "co": 27,
    "ni": 28,
    "cu": 29,
    "zn": 30,
}

ELEMENT_NAMES = {
    0: "Neutron",
    1: "Hydrogen",
    2: "Helium",
    3: "Lithium",
    4: "Beryllium",
    5: "Boron",
    6: "Carbon",
    7: "Nitrogen",
    8: "Oxygen",
    9: "Fluorine",
    10: "Neon",
    11: "Sodium",
    12: "Magnesium",
    13: "Aluminum",
    14: "Silicon",
    15: "Phosphorus",
    16: "Sulfur",
    17: "Chlorine",
    18: "Argon",
    19: "Potassium",
    20: "Calcium",
    21: "Scandium",
    22: "Titanium",
    23: "Vanadium",
    24: "Chromium",
    25: "Manganese",
    26: "Iron",
    27: "Cobalt",
    28: "Nickel",
    29: "Copper",
    30: "Zinc",
}

APPROX21_BASE_ISOS = [
    "h1",
    "he3",
    "he4",
    "c12",
    "n14",
    "o16",
    "ne20",
    "mg24",
    "si28",
    "s32",
    "ar36",
    "ca40",
    "ti44",
    "cr48",
    "fe52",
    "fe54",
    "fe56",
    "ni56",
    "neut",
    "prot",
]


def isotope_name(element, mass):
    if element == "neut":
        return "neut"
    return f"{element}{mass}"


def parse_isotope_name(name):
    name = name.strip().lower()
    if name == "prot":
        name = "h1"
    if name == "neut":
        return "neut", 1

    match = re.fullmatch(r"([a-z]+)([0-9]+)", name)
    if match is None:
        raise ValueError(f"invalid isotope name {name!r}")

    return match.group(1), int(match.group(2))


def add_isotope(isotopes, element, mass):
    if element not in ELEMENT_Z:
        raise ValueError(f"unknown element {element!r}")

    Z = ELEMENT_Z[element]
    N = 1 if element == "neut" else mass - Z
    isotopes[isotope_name(element, mass)] = (element, Z, N)


def add_isotope_by_name(isotopes, name):
    element, mass = parse_isotope_name(name)
    add_isotope(isotopes, element, mass)


def add_approx21_isotopes(isotopes, ye_iso_name, plus_co56):
    for name in APPROX21_BASE_ISOS:
        add_isotope_by_name(isotopes, name)
    if plus_co56:
        add_isotope_by_name(isotopes, "co56")
    add_isotope_by_name(isotopes, ye_iso_name)


def parse_mesa_net(path):
    isotopes = {}

    for raw_line in Path(path).read_text().splitlines():
        line = raw_line.split("!", 1)[0].strip()
        if not line or line in {"(", ")"} or line.startswith("add_isos_and_reactions"):
            continue

        approx21_match = re.fullmatch(r"(approx21|approx21_plus_co56)\(([^)]+)\)", line.replace(" ", ""))
        if approx21_match is not None:
            net_name, ye_iso_name = approx21_match.groups()
            add_approx21_isotopes(isotopes, ye_iso_name,
                                  net_name == rf"22 iso")
            continue

        tokens = line.replace("(", " ").replace(")", " ").split()
        if not tokens:
            continue

        element = tokens[0].lower()
        if element == "neut":
            add_isotope(isotopes, "neut", 1)
        elif element in ELEMENT_Z:
            masses = [int(token) for token in tokens[1:] if token.isdigit()]
            if len(masses) == 2 and masses[1] >= masses[0]:
                masses = list(range(masses[0], masses[1] + 1))
            for mass in masses:
                add_isotope(isotopes, element, mass)
        else:
            add_isotope_by_name(isotopes, element)

    return isotopes


def parse_store_net_info(path, isotope_names):
    special_reactions = {
        "r_h2_h2_to_he4": [("h2", "he4")],
        "r_he4_to_h2_h2": [("h2", "he4")],
        "r_c12_to_he4_he4_he4": [("he4", "c12")],
        "r_he4_he4_he4_to_c12": [("he4", "c12")],
        "r_h1_na23_to_c12_c12": [("na23", "c12")],
        "r_c12_c12_to_h1_na23": [("na23", "c12")],
        "r_h1_p31_to_o16_o16": [("o16", "p31")],
        "r_o16_o16_to_h1_p31": [("o16", "p31")],
        "r_he4_ne20_to_c12_c12": [("ne20", "c12")],
        "r_c12_c12_to_he4_ne20": [("ne20", "c12")],
        "r_he4_si28_to_o16_o16": [("si28", "o16")],
        "r_o16_o16_to_he4_si28": [("si28", "o16")],
        "r_neut_be7_to_he4_he4": [("be7", "neut"), ("be7", "he4"), ("he4", "neut")],
        "r_he4_he4_to_neut_be7": [("be7", "neut"), ("be7", "he4"), ("he4", "neut")],
        "r_neut_he3_to_h2_h2": [("neut", "he3"), ("he3", "h2")],
        "r_h2_h2_to_neut_he3": [("neut", "he3"), ("he3", "h2")],
        "r_neut_he4_he4_to_be9": [("neut", "be9"), ("neut", "he4"), ("he4", "be9")],
        "r_be9_to_neut_he4_he4": [("neut", "be9"), ("neut", "he4"), ("he4", "be9")],
        "r_neut_mg23_to_c12_c12": [("mg23", "c12")],
        "r_c12_c12_to_neut_mg23": [("mg23", "c12")],
        "r_neut_s31_to_o16_o16": [("s31", "o16")],
        "r_o16_o16_to_neut_s31": [("s31", "o16")],
        "r_h1_b11_to_he4_he4_he4": [("b11", "he4"), ("he4", "h1")],
        "r_he4_he4_he4_to_h1_b11": [("b11", "he4"), ("he4", "h1")],
        "r_h1_h1_he4_to_he3_he3": [("he4", "he3"), ("he3", "h1")],
        "r_he3_he3_to_h1_h1_he4": [("he4", "he3"), ("he3", "h1")],
        "r_h2_he4_he4_to_h1_be9": [("h2", "h1"), ("he4", "h1"), ("he4", "be9")],
        "r_h1_be9_to_h2_he4_he4": [("h2", "h1"), ("he4", "h1"), ("he4", "be9")],
        "r_h2_li6_to_h1_li7": [("li7", "h2"), ("li7", "li6"), ("h1", "h2"), ("h1", "li6")],
        "r_h1_li7_to_h2_li6": [("li7", "h2"), ("li7", "li6"), ("h1", "h2"), ("h1", "li6")],
        "r_h2_li6_to_neut_be7": [("neut", "li6"), ("neut", "h2"), ("be7", "li6"), ("be7", "h2")],
        "r_neut_be7_to_h2_li6": [("neut", "li6"), ("neut", "h2"), ("be7", "li6"), ("be7", "h2")],
        "r_h2_li7_to_neut_he4_he4": [("li7", "neut"), ("li7", "he4"), ("h2", "neut"), ("h2", "he4")],
        "r_neut_he4_he4_to_h2_li7": [("li7", "neut"), ("li7", "he4"), ("h2", "neut"), ("h2", "he4")],
        "r_he3_be7_to_h1_h1_he4_he4": [("he3", "he4"), ("he3", "h1"), ("be7", "h1"), ("be7", "he4")],
        "r_h1_h1_he4_he4_to_he3_be7": [("he3", "he4"), ("he3", "h1"), ("be7", "h1"), ("be7", "he4")],
        "r_h1_he4_he4_to_h2_be7": [("h2", "h1"), ("h1", "he4"), ("be7", "h1"), ("be7", "he4")],
        "r_h2_be7_to_h1_he4_he4": [("h2", "h1"), ("h1", "he4"), ("be7", "h1"), ("be7", "he4")],
        "r_he4_si28_to_c12_ne20": [("si28", "c12"), ("si28", "ne20")],
        "r_c12_ne20_to_he4_si28": [("si28", "c12"), ("si28", "ne20")],
        "r_h1_p31_to_c12_ne20": [("p31", "c12"), ("p31", "ne20")],
        "r_c12_ne20_to_h1_p31": [("p31", "c12"), ("p31", "ne20")],
        "r_h1_he4_he4_to_neut_b8": [("h1", "neut"), ("he4", "neut"), ("b8", "h1"), ("b8", "he4")],
        "r_neut_b8_to_h1_he4_he4": [("h1", "neut"), ("he4", "neut"), ("b8", "h1"), ("b8", "he4")],
        "r_neut_h1_h1_to_h1_h2": [("neut", "h1"), ("h1", "h2"), ("h2", "neut")],
        "r_h1_h2_to_neut_h1_h1": [("neut", "h1"), ("h1", "h2"), ("h2", "neut")],
        "r_h1_he4_to_h2_he3": [("h1", "h2"), ("h1", "he3"), ("he4", "h2"), ("he4", "he3")],
        "r_h2_he3_to_h1_he4": [("h1", "h2"), ("h1", "he3"), ("he4", "h2"), ("he4", "he3")],
        "r_h2_c13_to_neut_n14": [("c13", "n14"), ("c13", "neut"), ("h2", "neut"), ("h2", "n14")],
        "r_neut_n14_to_h2_c13": [("c13", "n14"), ("c13", "neut"), ("h2", "neut"), ("h2", "n14")],
        "r_neut_s31_to_c12_ne20": [("s31", "c12"), ("s31", "ne20")],
        "r_c12_ne20_to_neut_s31": [("s31", "c12"), ("s31", "ne20")],
        "r_c12_o16_to_he4_mg24": [("c12", "mg24"), ("o16", "mg24")],
        "r_he4_mg24_to_c12_o16": [("c12", "mg24"), ("o16", "mg24")],
        "r_c12_o16_to_neut_si27": [("c12", "si27"), ("o16", "si27")],
        "r_neut_si27_to_c12_o16": [("c12", "si27"), ("o16", "si27")],
        "r_h1_al27_to_c12_o16": [("al27", "c12"), ("al27", "o16")],
        "r_c12_o16_to_h1_al27": [("al27", "c12"), ("al27", "o16")],
        "r_li6_to_neut_h1_he4": [("li6", "neut"), ("li6", "h1"), ("li6", "he4")],
        "r_neut_h1_he4_to_li6": [("li6", "neut"), ("li6", "h1"), ("li6", "he4")],
        "r_he3_li7_to_neut_h1_he4_he4": [("he3", "h1"), ("he3", "he4"), ("he3", "neut"), ("li7", "neut"), ("li7", "h1"), ("li7", "he4")],
        "r_b8_wk_he4_he4": [("b8", "he4")],
        "r_h1_he3_wk_he4": [("h1", "he4"), ("he3", "he4")],
        "r_h1_h1_ec_h2": [("h1", "h2")],
        "r_h1_h1_wk_h2": [("h1", "h2")],
    }

    edges = set()

    def add_edge(iso1, iso2):
        try:
            element1, mass1 = parse_isotope_name(iso1)
            element2, mass2 = parse_isotope_name(iso2)
        except ValueError:
            return

        iso1 = isotope_name(element1, mass1)
        iso2 = isotope_name(element2, mass2)
        if iso1 in isotope_names and iso2 in isotope_names and iso1 != iso2:
            edges.add(tuple(sorted((iso1, iso2))))

    for raw_line in Path(path).read_text().splitlines():
        if "create rate data for" not in raw_line:
            continue

        reaction_id = raw_line.split()[-1]
        if reaction_id in special_reactions:
            for iso1, iso2 in special_reactions[reaction_id]:
                add_edge(iso1, iso2)
            continue

        parts = reaction_id.split("_")
        if len(parts) == 4:
            add_edge(parts[1], parts[3])

    return sorted(edges)


def plot_network(isotopes, edges, output_path=None, highlight_isotopes=None, highlight_label=None):

    fig, ax = plt.subplots(figsize=(12, 24))
    highlight_isotopes = highlight_isotopes or {}
    highlight_names = set(highlight_isotopes)
    visible_isotopes = dict(isotopes)
    visible_isotopes.update({
        name: data
        for name, data in highlight_isotopes.items()
        if name not in visible_isotopes
    })

    positions = {
        name: (N - Z, Z)
        for name, (_, Z, N) in isotopes.items()
    }

    for iso1, iso2 in edges:
        x1, y1 = positions[iso1]
        x2, y2 = positions[iso2]
        ax.plot([x1, x2], [y1, y2], "k-", lw=1, zorder=1)

    for name, (_, Z, N) in visible_isotopes.items():
        is_highlighted = name in highlight_names
        rect = patches.Rectangle(
            ((N - Z) - 0.3, Z - 0.25),
            0.6,
            0.5,
            linewidth=2,
            edgecolor="deeppink" if is_highlighted and name not in isotopes else "royalblue",
            facecolor="orchid" if is_highlighted else "darkblue",
            zorder=10,
        )
        ax.add_patch(rect)

    max_x_by_z = {}
    for _, Z, N in visible_isotopes.values():
        max_x_by_z[Z] = max(max_x_by_z.get(Z, N - Z), N - Z)

    for Z in sorted(max_x_by_z):
        ax.text(
            max(max_x_by_z[Z] + 1.0, 2.0),
            Z,
            ELEMENT_NAMES[Z],
            fontsize=26,
            ha="left",
            va="center",
            weight="bold",
        )

    if highlight_label is not None:
        ax.text(
            max(N - Z for _, Z, N in visible_isotopes.values()) - 0.2,
            14.6,
            rf"128 iso",
            fontsize=34,
            ha="center",
            va="center",
            weight="bold",
            color="darkblue",
        )
        ax.text(
            max(N - Z for _, Z, N in visible_isotopes.values()) - 0.2,
            13.5,
            highlight_label,
            fontsize=34,
            ha="center",
            va="center",
            weight="bold",
            color="orchid",
        )

    xs = [N - Z for _, Z, N in visible_isotopes.values()]
    zs = [Z for _, Z, _ in visible_isotopes.values()]
    ax.axvline(x=0, color="red", linestyle="--", lw=3)
    ax.text(1.4, max(zs) + 0.75, "N = Z", fontsize=30, ha="center", va="center", weight="bold", color="red")

    ax.set_xlabel("Neutrons (N) - Protons (Z)", fontsize=40)
    ax.set_ylabel("Proton Number (Z)", fontsize=40)
    ax.set_xlim(min(xs) - 2.5, max(xs) + 5.0)
    ax.set_ylim(min(zs) - 0.5, max(zs) + 1.25)
    ax.set_xticks([-3, 0, 5, 10, 15])
    ax.set_xticks([], minor=True)
    ax.set_yticks([], minor=True)
    ax.tick_params(axis="both", labelsize=30)
    ax.grid(False)

    if output_path:
        fig.tight_layout()
        fig.savefig(output_path, format="pdf")
    else:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    net_path = Path("../data/mesa_128.net")
    highlight_net_path = Path("../data/approx21_cr60_plus_co56.net")
    reactions_path = Path("../data/store_net_info.txt")
    output_path = Path("../manuscript/figures/network_128.pdf")

    isotopes = parse_mesa_net(net_path)
    highlight_isotopes = parse_mesa_net(highlight_net_path)
    edges = parse_store_net_info(reactions_path, set(isotopes))
    if len(isotopes) != 128:
        raise RuntimeError(f"expected 128 isotopes, found {len(isotopes)}")

    plot_network(
        isotopes,
        edges,
        output_path=output_path,
        highlight_isotopes=highlight_isotopes,
        highlight_label=rf"22 iso",
    )
    outsidex_net = sorted(set(highlight_isotopes) - set(isotopes))
    print(
        f"wrote {output_path} with {len(isotopes)} base isotopes, "
        f"{len(edges)} linkages, and {len(highlight_isotopes)} approx21 highlighted isotopes"
    )
    if outside_net:
        print(f"approx21 isotopes shown outside mesa_128.net: {', '.join(outside_net)}")
