"""ЛЕММАТИЗАТОР яванского языка (свой, на правилах; готового не существует).

Зачем: по инструкции эмбеддинги считаются по лемматизированному корпусу.
Яванская морфология богатая (nulis/nulisi/nulisake/ditulis/tinulis/
panulisan -- одно гнездо корня tulis), без лемматизации словарь корпуса
рассыпается и каждой форме достаётся меньше статистики.

Принцип (по образцу алгоритма Nazief-Adriani для индонезийского):
НЕ слепой стемминг, а "снять аффикс -> проверить по лексикону корней"
(lexicon/roots.txt, собран build_lexicon.py из словарей Horne 1974 и
списков dasanama). Поиск в ширину по цепочкам снятий (глубина <= 3):

  0. слово уже в лексиконе -> оно и есть лемма (консервативно: значит,
     лексикализованные производные вроде abangan остаются собой);
  1. редупликации: полная (omah-omah -> omah), с чередованием гласных
     (bola-bali -> bali, берём вторую часть), dwipurwa -- удвоение
     первого слога (lelaku -> laku, sesepuh -> sepuh);
  2. суффиксы (ngoko и krama): -ipun/-nipun, -ake/-aken, -ana, -na, -ne,
     -en, -an, -e, -i, -a, -ku, -mu; стиховые генитив -(n)ing
     (cihnaning -> cihna) и посессив -(n)ira (garwanira -> garwa);
  3. префиксы без мутации: dipun-, di-, ka-, ke-, tak-, dak-, kok-, sa-,
     pa-, pi-, pra-, a-, kuma-;
  4. назальный префикс N- (актив) с ВОССТАНОВЛЕНИЕМ первой согласной корня:
     ny- -> s/c (nyapu->sapu, nyekel->cekel), m- -> p/w (mangan->pangan,
     maca->waca), n- -> t/th (nulis->tulis), ng- -> k/гласная
     (ngarang->karang, ngombe->ombe), nge- + односложный корень
     (ngebom->bom); кластеры mb-/nd-/ngg-/nj- -> отпадает только назальный
     (mbalang->balang, nggawa->gawa);
  5. инфиксы -um-/-in- после первой согласной (gumuyu->guyu, tinulis->tulis).

Выбор из нескольких кандидатов: минимум снятий, затем частотность корня
в корпусе (lexicon/freq.tsv), затем длина корня. Если ни одна цепочка
не привела к известному корню -- слово остаётся как есть (ничего не ломаем;
собственные имена и кэ-формы вне словаря не трогаются).

Ограничения (задокументированы): не разворачиваются стяжения гласных на
стыке (turu+an -> turon), не переводится krama-лексика в ngoko (это
лексическое соответствие, не морфология), старое "j"=/y/ не нормализуется.

Оценка: python3 scripts/jav_lemmatizer.py --eval eval/jv_csui-ud-test.conllu
(трибанк UD Javanese-CSUI, золотые леммы; см. отчёт в README).
Как библиотека: from jav_lemmatizer import Lemmatizer; lem.lemma(tok).
"""
import os
import sys

LEXDIR = os.path.join(os.path.dirname(__file__), "..", "lexicon")

SUFFIXES = ["kaken", "nipun", "kake", "ipun", "aken", "ake", "ning",
            "nira", "ana", "ing", "ira", "na", "ne", "en", "an",
            "e", "i", "a", "ku", "mu"]
PREFIXES = ["dipun", "di", "ka", "ke", "tak", "dak", "kok", "sa",
            "pa", "pi", "pra", "kuma", "a"]
SPECIALS = {"ORDINAL1", "PRON1"}


def nasal_candidates(w):
    """Формы после снятия назального префикса N- (с восстановлением
    первой согласной корня)."""
    out = []
    if w.startswith("nj"):
        out.append(w[1:])                       # njupuk->jupuk
    elif w.startswith("nge") and len(w) <= 7:
        out.append(w[3:])                       # ngebom->bom (короткий корень)
    if w.startswith("ng"):
        out.append(w[2:])                       # ngombe->ombe
        out.append("k" + w[2:])                 # ngarang->karang
    elif w.startswith("ny"):
        out.append("s" + w[2:])                 # nyapu->sapu
        out.append("c" + w[2:])                 # nyekel->cekel
    elif w.startswith("mb") or (len(w) > 1 and w[0] == "m" and w[1] in "lr"):
        out.append(w[1:])                       # mbalang->balang, mlaku->laku
    elif w.startswith("m"):
        out.append("p" + w[1:])                 # mangan->pangan
        out.append("w" + w[1:])                 # maca->waca
    elif w.startswith("nd"):
        out.append(w[1:])                       # ndelok->delok
    elif w.startswith("n"):
        out.append("t" + w[1:])                 # nulis->tulis
        out.append("th" + w[1:])                # nuthuk->thuthuk
    return out


def strip_candidates(w):
    """Все формы, получаемые ОДНИМ снятием (суффикс/префикс/назальный/
    инфикс/редупликация)."""
    out = []
    if "-" in w:
        parts = w.split("-")
        if len(parts) == 2 and parts[0] and parts[1]:
            if parts[0] == parts[1]:
                out.append(parts[1])            # omah-omah -> omah
            elif len(parts[0]) == len(parts[1]):
                out.append(parts[1])            # bola-bali -> bali
        return out                              # с дефисом -- только редуп.
    if len(w) > 4 and w[0] == w[2] and w[1] in "ea":
        out.append(w[2:])                       # dwipurwa: lelaku -> laku
    for s in SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= 3:
            out.append(w[:-len(s)])
    for p in PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 3:
            out.append(w[len(p):])
    out.extend(c for c in nasal_candidates(w) if len(c) >= 3)
    if len(w) >= 5 and w[1:3] in ("um", "in"):
        out.append(w[0] + w[3:])                # gumuyu->guyu, tinulis->tulis
    return out


class Lemmatizer:
    def __init__(self, lexdir=LEXDIR):
        self.roots = set(
            open(os.path.join(lexdir, "roots.txt"), encoding="utf-8")
            .read().split())
        self.freq = {}
        fp = os.path.join(lexdir, "freq.tsv")
        if os.path.exists(fp):
            for ln in open(fp, encoding="utf-8"):
                w, c = ln.rsplit("\t", 1)
                self.freq[w] = int(c)
        # очень частотные КОРОТКИЕ слова корпуса -- де-факто лексические
        # единицы (служебные kene/mula/saiki...), даже если словари их не
        # дали; длинные частотные формы (anggitanipun) -- к анализу
        self.roots |= {w for w, c in self.freq.items()
                       if c >= 3000 and 3 <= len(w) <= 7 and w.isalpha()}
        self.cache = {}

    def lemma(self, tok):
        if tok in SPECIALS or len(tok) < 4 or tok in self.roots:
            return tok
        # очень частотные КОРОТКИЕ слова вне лексикона -- служебные (nganti,
        # saiki...): не трогаем, им положен собственный вектор. Длинные
        # частотные формы (anggitanipun) -- обычная морфология, анализируем.
        if self.freq.get(tok, 0) >= 5000 and len(tok) <= 7:
            return tok
        if tok in self.cache:
            return self.cache[tok]
        # поиск в ширину: frontier -- формы после depth снятий.
        # Глубина <= 3 (pa+N+root+an); глубже начинают калечиться
        # имена собственные (natakusuma -> usum)
        best, frontier, seen = None, [tok], {tok}
        for depth in range(1, 4):
            nxt = []
            for w in frontier:
                for c in strip_candidates(w):
                    if c in seen or len(c) < 3:
                        continue
                    seen.add(c)
                    nxt.append(c)
            # трёхбуквенный корень принимаем только частотный: в dasanama
            # есть редкие кави-слога ("pul", "ken"), ломающие всё подряд
            hits = [c for c in nxt if c in self.roots and
                    (len(c) >= 4 or self.freq.get(c, 0) >= 500)]
            if hits:
                best = max(hits, key=lambda c: (self.freq.get(c, 0), len(c)))
                break
            frontier = nxt
            if not frontier:
                break
        res = best if best else tok
        self.cache[tok] = res
        return res


# ----------------------------------------------------------------- оценка --
def evaluate(conllu_path):
    sys.path.insert(0, os.path.dirname(__file__))
    from clean_corpus import normalize
    lem = Lemmatizer()
    total = correct = 0
    affixed = affixed_correct = 0
    errors = {}
    for ln in open(conllu_path, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        cols = ln.split("\t")
        if len(cols) != 10 or not cols[0].isdigit():
            continue
        form, gold = cols[1].lower(), cols[2].lower()
        if not form.isalpha() or cols[3] in ("PUNCT", "SYM", "NUM", "PROPN"):
            continue
        form_n, gold_n = normalize(form), normalize(gold)
        pred = lem.lemma(form_n)
        total += 1
        if pred == gold_n:
            correct += 1
        else:
            errors[(form_n, gold_n, pred)] = errors.get(
                (form_n, gold_n, pred), 0) + 1
        if form_n != gold_n:
            affixed += 1
            affixed_correct += pred == gold_n
    print(f"всего токенов:      {total}")
    print(f"точность:           {correct / total:.3f}")
    print(f"аффиксированных:    {affixed} "
          f"(точность на них: {affixed_correct / affixed:.3f})")
    print("\nчастые ошибки (форма -> золото / наш ответ):")
    for (f, g, p), c in sorted(errors.items(), key=lambda x: -x[1])[:25]:
        print(f"  {c:4d}  {f} -> {g} / {p}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--eval":
        evaluate(sys.argv[2])
    else:
        print(__doc__)
