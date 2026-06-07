"""
benchmark.py - Comparaison des 3 approches de calcul
Projet 2 - 6e TTR Informatique - CEPES Jodoigne

Scenarios :
  1. Python pur      : calcul IMC sans DLL, tout en Python
  2. ctypes scalaire : appel C un par un en boucle Python
  3. ctypes batch    : appel C sur tout le tableau en une passe

Utilisation :
  python benchmark.py
  python benchmark.py --n 50000
"""

import ctypes
import time
import random
import sys

import module

# ===============================================================
#  CONFIG
# ===============================================================

N_DEFAULT  = 100_000
WEIGHT_MIN = 45.0
WEIGHT_MAX = 120.0
HEIGHT_MIN = 1.50
HEIGHT_MAX = 2.00

# Affiche la progression toutes les X iterations
PROGRESS_STEP = 10_000


# ===============================================================
#  BARRE DE PROGRESSION
# ===============================================================

def progress(label: str, current: int, total: int, start: float):
    """Affiche une barre de progression sur la meme ligne."""
    pct      = current / total
    filled   = int(pct * 30)
    bar      = "#" * filled + "-" * (30 - filled)
    elapsed  = time.perf_counter() - start
    print(f"\r  {label} [{bar}] {pct*100:5.1f}%  {elapsed:.3f}s",
          end="", flush=True)


def progress_done(label: str, elapsed: float):
    """Affiche la ligne finale quand un scenario est termine."""
    bar = "#" * 30
    print(f"\r  {label} [{bar}] 100.0%  {elapsed:.4f}s  OK",
          flush=True)


# ===============================================================
#  GENERATION DES DONNEES
# ===============================================================

def generate_data(n: int):
    print(f"\n  Generation de {n:,} elements...", flush=True)

    weights_py = [random.uniform(WEIGHT_MIN, WEIGHT_MAX) for _ in range(n)]
    heights_py = [random.uniform(HEIGHT_MIN, HEIGHT_MAX) for _ in range(n)]

    FloatArray = ctypes.c_float * n
    weights_c  = FloatArray(*weights_py)
    heights_c  = FloatArray(*heights_py)
    results_c  = FloatArray(*([0.0] * n))

    print(f"  Generation terminee.\n", flush=True)
    return weights_py, heights_py, weights_c, heights_c, results_c


# ===============================================================
#  SCENARIO 1 - PYTHON PUR
# ===============================================================

def scenario_python_pur(weights: list, heights: list, n: int):
    """Calcul IMC en Python pur, avec progression live."""
    label   = "1. Python pur      "
    results = []
    start   = time.perf_counter()

    for i, (w, h) in enumerate(zip(weights, heights)):
        results.append(w / (h * h))
        if (i + 1) % PROGRESS_STEP == 0:
            progress(label, i + 1, n, start)

    elapsed = time.perf_counter() - start
    progress_done(label, elapsed)
    return elapsed, results


# ===============================================================
#  SCENARIO 2 - CTYPES SCALAIRE
# ===============================================================

def scenario_ctypes_scalaire(weights: list, heights: list, n: int):
    """Appel C un par un avec progression live."""
    label   = "2. ctypes scalaire "
    results = []
    start   = time.perf_counter()

    for i, (w, h) in enumerate(zip(weights, heights)):
        results.append(
            module.lib.calc_bmi(ctypes.c_float(w), ctypes.c_float(h))
        )
        if (i + 1) % PROGRESS_STEP == 0:
            progress(label, i + 1, n, start)

    elapsed = time.perf_counter() - start
    progress_done(label, elapsed)
    return elapsed, results


# ===============================================================
#  SCENARIO 3 - CTYPES BATCH
# ===============================================================

def scenario_ctypes_batch(weights_c, heights_c, results_c, n: int):
    """Un seul appel C pour tout le tableau."""
    label = "3. ctypes batch    "

    print(f"\r  {label} [{'.' * 30}] en cours...",
          end="", flush=True)

    start = time.perf_counter()
    module.lib.calc_bmi_batch(weights_c, heights_c, results_c, ctypes.c_int(n))
    elapsed = time.perf_counter() - start

    progress_done(label, elapsed)
    return elapsed, list(results_c)


# ===============================================================
#  VERIFICATION DE COHERENCE
# ===============================================================

def verify_results(r1: list, r2: list, r3: list, tolerance=0.01):
    errors = 0
    for v1, v2, v3 in zip(r1, r2, r3):
        if abs(v1 - v2) > tolerance or abs(v1 - v3) > tolerance:
            errors += 1

    if errors == 0:
        print(f"  Verification : OK (tolerance {tolerance})")
    else:
        print(f"  Verification : {errors} differences > {tolerance} detectees")


# ===============================================================
#  TABLEAU FINAL
# ===============================================================

def print_results(n: int, t1: float, t2: float, t3: float):
    print()
    print("=" * 60)
    print(f"  RESULTATS - {n:,} elements")
    print("=" * 60)
    print(f"  {'Scenario':<25} {'Temps (s)':>10} {'Ratio':>10}")
    print(f"  {'-' * 47}")
    print(f"  {'1. Python pur':<25} {t1:>10.4f} {'(reference)':>10}")
    print(f"  {'2. ctypes scalaire':<25} {t2:>10.4f} {t1/t2:>9.1f}x")
    print(f"  {'3. ctypes batch':<25} {t3:>10.4f} {t1/t3:>9.1f}x")
    print("=" * 60)
    print()


# ===============================================================
#  SCRIPT PRINCIPAL
# ===============================================================

def main():
    n = N_DEFAULT
    if "--n" in sys.argv:
        idx = sys.argv.index("--n")
        if idx + 1 < len(sys.argv):
            try:
                n = int(sys.argv[idx + 1])
            except ValueError:
                print("Valeur --n invalide, utilisation du defaut.")

    module.init_db()
    module.build_met_table()

    weights_py, heights_py, weights_c, heights_c, results_c = generate_data(n)

    print("  Lancement des scenarios...\n")

    t1, r1 = scenario_python_pur(weights_py, heights_py, n)
    t2, r2 = scenario_ctypes_scalaire(weights_py, heights_py, n)
    t3, r3 = scenario_ctypes_batch(weights_c, heights_c, results_c, n)

    print()
    verify_results(r1, r2, r3)

    print_results(n, t1, t2, t3)


if __name__ == "__main__":
    main()