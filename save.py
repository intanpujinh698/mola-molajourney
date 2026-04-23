# ============================================================
#  save.py — Highscore & Save System
# ============================================================
import json
import os
from settings import SAVE_FILE


DEFAULT_DATA = {
    'highscore': 0,
    'total_games': 0,
    'total_jellies': 0,
    'best_size': 1.0,
}


def load() -> dict:
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                # pastikan semua key ada (backward compat)
                for k, v in DEFAULT_DATA.items():
                    data.setdefault(k, v)
                return data
        except Exception:
            pass
    return dict(DEFAULT_DATA)


def save(data: dict):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f'[Save] Gagal menyimpan: {e}')


def update_after_game(score: int, best_size: float) -> dict:
    """Panggil saat game over. Kembalikan data terupdate."""
    data = load()
    data['total_games']   += 1
    data['total_jellies'] += score
    if score > data['highscore']:
        data['highscore'] = score
    if best_size > data['best_size']:
        data['best_size'] = round(best_size, 2)
    save(data)
    return data
