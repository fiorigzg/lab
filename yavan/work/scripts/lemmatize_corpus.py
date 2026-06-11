"""ЛЕММАТИЗАЦИЯ очищенного корпуса (corpus_clean -> corpus_lemma).

Зачем: финальный шаг обработки по инструкции -- эмбеддинги (SVD, CBoW)
считаются по очищенному И лемматизированному корпусу. Очистка уже сделана
(clean_corpus.py); этот скрипт применяет лемматизатор (jav_lemmatizer.py,
лексикон из build_lexicon.py) к каждому токену и сохраняет корпус в той же
структуре:

  corpus_lemma/texts/<ведро>/<имя>.txt   -- 1 предложение = 1 строка;
  corpus_lemma/corpus_text_<ведро>.txt   -- 1 строка = 1 текст (для SVD);
  corpus_lemma/corpus_segments_<ведро>.txt -- 1 строка = 1 предложение (CBoW);
  corpus_lemma/_stats.txt -- статистика, в т.ч. сжатие словаря
     (сколько разных токенов было до и стало после лемматизации).

Токены-замены ORDINAL1/PRON1 не трогаются. Слова, для которых не нашлось
корня в лексиконе, остаются как есть (см. принципы в jav_lemmatizer.py).

Запуск: python3 scripts/lemmatize_corpus.py (из work/, после
clean_corpus.py и build_lexicon.py). corpus_lemma/ перезаписывается.
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from jav_lemmatizer import Lemmatizer  # noqa: E402

SRC = "corpus_clean"
OUT = "corpus_lemma"
BUCKETS = ("sastra", "arsip", "jurnal", "majalah")


def main():
    lem = Lemmatizer()
    os.makedirs(OUT, exist_ok=True)
    stats = Counter()
    vocab_before = {b: set() for b in BUCKETS}
    vocab_after = {b: set() for b in BUCKETS}
    for b in BUCKETS:
        srcdir = os.path.join(SRC, "texts", b)
        if not os.path.isdir(srcdir):
            continue
        outdir = os.path.join(OUT, "texts", b)
        os.makedirs(outdir, exist_ok=True)
        ct = open(os.path.join(OUT, f"corpus_text_{b}.txt"), "w",
                  encoding="utf-8")
        cs = open(os.path.join(OUT, f"corpus_segments_{b}.txt"), "w",
                  encoding="utf-8")
        for fn in sorted(os.listdir(srcdir)):
            text_sents = []
            for ln in open(os.path.join(srcdir, fn), encoding="utf-8"):
                toks = ln.split()
                lemmas = [lem.lemma(t) for t in toks]
                vocab_before[b].update(toks)
                vocab_after[b].update(lemmas)
                stats[b + "_tokens"] += len(lemmas)
                stats[b + "_changed"] += sum(
                    1 for t, l in zip(toks, lemmas) if t != l)
                text_sents.append(" ".join(lemmas))
            with open(os.path.join(outdir, fn), "w", encoding="utf-8") as f:
                f.write("\n".join(text_sents) + "\n")
            ct.write(" ".join(text_sents) + "\n")
            cs.write("\n".join(text_sents) + "\n")
            stats[b + "_files"] += 1
            stats[b + "_sents"] += len(text_sents)
        ct.close()
        cs.close()
        print(f"{b}: готово", flush=True)
    with open(os.path.join(OUT, "_stats.txt"), "w", encoding="utf-8") as f:
        for k in sorted(stats):
            f.write(f"{k}: {stats[k]}\n")
        for b in BUCKETS:
            if vocab_before[b]:
                f.write(f"{b}_vocab: {len(vocab_before[b])} -> "
                        f"{len(vocab_after[b])}\n")
    for b in BUCKETS:
        if vocab_before[b]:
            print(f"{b}: словарь {len(vocab_before[b])} -> "
                  f"{len(vocab_after[b])} типов; заменено "
                  f"{stats[b + '_changed']} из {stats[b + '_tokens']} токенов")


if __name__ == "__main__":
    main()
