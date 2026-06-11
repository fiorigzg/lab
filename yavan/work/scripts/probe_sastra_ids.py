"""ДОБОР sastra.org перебором ID статей (финальная проверка полноты).

Зачем: листинги категорий живого сайта рендерятся JS и через прокси не
видны, а Wayback CDX покрывает не всё. Joomla отдаёт статью по чистому ID:
  https://www.sastra.org/index.php?option=com_content&view=article&id=N
ID статей последовательные; перебираем все N от 1 до max(известных)+,
которых нет среди скачанных файлов (список /tmp/cand_ids.txt готовится
в check-скрипте/вручную).

Категорию страница в этом виде не сообщает, поэтому добранные статьи
складываются в corpus_raw/sastra-org/_recovered/; при очистке они
распределяются по вёдрам по названию (Kajawèn / Pusaka Jawi -> jurnal,
"Koleksi Warsadiningrat" и пр. -> arsip, иначе sastra).

Выход: corpus_raw/sastra-org/_recovered/<id>-<slug>.txt,
строки в _metadata_live.tsv (категория = "_recovered").
Запуск: python3 scripts/probe_sastra_ids.py; резюме через _probed_ids.txt.
"""
import os
import re
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
from download_sastra_live import fetch_jina, md_to_text  # noqa: E402
from download_sastra_org import OUT  # noqa: E402

REC = os.path.join(OUT, "_recovered")
META = os.path.join(OUT, "_metadata_live.tsv")
PROBED = os.path.join(OUT, "_probed_ids.txt")
NONSEF = "https://www.sastra.org/index.php?option=com_content&view=article&id="

os.makedirs(REC, exist_ok=True)
io_lock = threading.Lock()


def slugify(title):
    s = re.sub(r"[^\w]+", "-", title.lower()).strip("-")
    return s[:120] or "untitled"


def probe(art_id):
    code, md = fetch_jina(NONSEF + str(art_id))
    status = "fail:" + code
    if code == "200":
        title, text = md_to_text(md)
        if not title or title.startswith(("Error", "Wulang", "404")) and not text:
            status = "404/empty"
        elif len(text) > 200:
            fname = f"{art_id}-{slugify(title)}.txt"
            with open(os.path.join(REC, fname), "w", encoding="utf-8") as f:
                f.write(title + "\n" + text + "\n")
            with io_lock:
                with open(META, "a", encoding="utf-8") as f:
                    f.write(f"_recovered\t{fname[:-4]}\t{title}\t"
                            f"{NONSEF}{art_id}\tlive\t_recovered/{fname}\t"
                            f"{len(text)}\n")
            status = "saved"
        else:
            status = "no-text"
    with io_lock:
        with open(PROBED, "a", encoding="utf-8") as f:
            f.write(f"{art_id}\t{status}\n")
        if status == "saved":
            print(art_id, status, flush=True)
    time.sleep(6)  # r.jina.ai без ключа ~20 зап/мин; быстрее -> обрывы (код 000)


def main():
    cand = [int(x) for x in open("/tmp/cand_ids.txt").read().split()]
    done = set()
    if os.path.exists(PROBED):
        done = {int(l.split("\t")[0]) for l in open(PROBED) if l.strip()}
    todo = [i for i in cand if i not in done]
    print(f"probing {len(todo)} ids", flush=True)
    with ThreadPoolExecutor(max_workers=1) as pool:
        list(pool.map(probe, todo))
    print("done", flush=True)


if __name__ == "__main__":
    main()
