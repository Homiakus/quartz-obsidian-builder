# dataview_converter.py
import re
from pathlib import Path
import shutil
import yaml

# Регулярка для нахождения блоков ```dataview ... ```
DATABLOCK_RE = re.compile(r"```dataview(.*?)```", re.DOTALL | re.IGNORECASE)

def _read_file(path: Path):
    return path.read_text(encoding="utf-8")

def _write_file(path: Path, content: str):
    path.write_text(content, encoding="utf-8")

def _extract_frontmatter(text: str):
    """
    Возвращает dict или {}. Ищет YAML frontmatter между --- (начало файла).
    """
    if text.startswith("---"):
        parts = text.split("---", 2)
        # parts: ['', yaml, rest] или ['', yaml, rest]
        if len(parts) >= 3:
            try:
                data = yaml.safe_load(parts[1])
                return data or {}
            except Exception:
                return {}
    return {}

def _extract_inline_kv(text: str):
    """
    Ищет строки вида Key:: Value в теле файла и возвращает dict.
    """
    res = {}
    for line in text.splitlines():
        if "::" in line:
            parts = line.split("::", 1)
            key = parts[0].strip()
            val = parts[1].strip()
            res[key] = val
    return res

def _gather_files(vault_root: Path, from_path: str = None):
    """
    Возвращает список Path объектов .md в vault_root (или в поддиректории from_path).
    """
    if from_path:
        # normalize and strip quotes
        from_path = from_path.strip().strip('"').strip("'")
        target = vault_root / from_path
        if target.exists() and target.is_dir():
            base = target
        else:
            # возможно пользователь указал имя папки без точного совпадения -> ищем поддеревья
            candidate = vault_root / from_path
            base = candidate if candidate.exists() else vault_root
    else:
        base = vault_root
    return list(base.rglob("*.md"))

def _value_for_column(md_text: str, col: str, file_path: Path, vault_root: Path):
    col = col.strip()
    # быстрые псевдо-поля
    if col.lower() in ("file.name", "file"):
        return file_path.stem
    if col.lower() in ("file.path", "path"):
        return str(file_path.relative_to(vault_root))
    # берем frontmatter, затем inline
    fm = _extract_frontmatter(md_text)
    inline = _extract_inline_kv(md_text)
    # priority: frontmatter -> inline -> fallback empty
    if col in fm:
        return str(fm.get(col))
    if col in inline:
        return inline.get(col)
    # иногда запросы про title
    if col.lower() in ("title", "name"):
        if "title" in fm:
            return fm["title"]
        return file_path.stem
    # если ничего - пусто
    return ""

def _render_md_table(headers, rows):
    # headers: list[str], rows: list[list[str]]
    hdr = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = "\n".join("| " + " | ".join(row) + " |" for row in rows)
    return f"\n{hdr}\n{sep}\n{body}\n"

def _render_md_list(items):
    return "\n" + "\n".join(f"- {it}" for it in items) + "\n"

def convert_dataview_in_vault(vault_root: str, backup: bool = True, logger=print):
    """
    Проходит по всем .md, заменяет dataview-блоки на статический md.
    """
    vault = Path(vault_root)
    if not vault.exists():
        raise FileNotFoundError("Vault не найден: " + vault_root)
    md_files = list(vault.rglob("*.md"))
    logger(f"Найдено {len(md_files)} md файлов в {vault_root}")

    for fp in md_files:
        text = _read_file(fp)
        changed = False

        def _process_block(match):
            nonlocal changed
            block = match.group(1).strip()
            lines = block.splitlines()
            if not lines:
                return match.group(0)  # без изменений
            first = lines[0].strip()
            # Разбираем TABLE
            if first.upper().startswith("TABLE"):
                # пытаемся найти FROM (простая стратегия)
                parts = re.split(r"\bFROM\b", first, flags=re.IGNORECASE)
                cols_part = parts[0].strip()[5:].strip()  # после 'TABLE'
                cols = [c.strip() for c in cols_part.split(",") if c.strip()]
                from_path = None
                if len(parts) > 1:
                    # может быть 'FROM "folder/sub" WHERE ...' -> возьмём только первую часть после FROM
                    right = parts[1].strip()
                    # удалим WHERE/SORT если есть
                    right = re.split(r"\bWHERE\b|\bSORT\b", right, flags=re.IGNORECASE)[0].strip()
                    # strip quotes
                    from_path = right.strip().strip('"').strip("'")
                # соберём файлы
                files = _gather_files(vault, from_path)
                rows = []
                for f in files:
                    ftext = _read_file(f)
                    row = []
                    for col in cols:
                        val = _value_for_column(ftext, col, f, vault)
                        # безопасно экранируем pipe
                        val = val.replace("|", "\\|")
                        row.append(val or "")
                    rows.append(row)
                if not cols:
                    return match.group(0)
                md_table = _render_md_table(cols, rows)
                changed = True
                logger(f"Converted TABLE (from={from_path}) in {fp}")
                return md_table

            # Разбираем LIST
            if first.upper().startswith("LIST"):
                parts = re.split(r"\bFROM\b", first, flags=re.IGNORECASE)
                from_path = None
                if len(parts) > 1:
                    right = parts[1].strip()
                    right = re.split(r"\bWHERE\b|\bSORT\b", right, flags=re.IGNORECASE)[0].strip()
                    from_path = right.strip().strip('"').strip("'")
                files = _gather_files(vault, from_path)
                items = []
                for f in files:
                    ftext = _read_file(f)
                    title = _value_for_column(ftext, "title", f, vault) or f.stem
                    rel = str(f.relative_to(vault))
                    items.append(f"[{title}]({rel})")
                md_list = _render_md_list(items)
                changed = True
                logger(f"Converted LIST (from={from_path}) in {fp}")
                return md_list

            # Для датавью js или сложных случаев — просто оставляем неприкосновенным
            logger(f"Пропущен сложный dataview блок в {fp}; требуется dataviewjs или сложный парсинг.")
            return match.group(0)

        new_text = DATABLOCK_RE.sub(_process_block, text)
        if changed:
            if backup:
                bak = fp.with_suffix(fp.suffix + ".bak")
                shutil.copy2(fp, bak)
                logger(f"Backup сделан: {bak}")
            _write_file(fp, new_text)
            logger(f"Файл обновлён: {fp}")

    return "Конвертация Dataview завершена"
