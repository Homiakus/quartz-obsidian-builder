# quartz.py
import os
import subprocess
import shutil
from pathlib import Path

from git_utils import git_clone, git_pull

def ensure_quartz_cloned_and_setup(repo_url: str, local_path: str, logger=print):
    """
    Если local_path не существует -> git clone repo_url local_path
    Иначе -> git pull
    Также выполняет `npm install` при первом клонировании (по желанию).
    """
    lp = Path(local_path)
    if not lp.exists():
        logger(f"Cloning Quartz from {repo_url} → {local_path} ...")
        git_clone(repo_url, local_path)
        # После клонирования — рекомендуем установить зависимости
        logger("Устанавливаем node зависимости: npm install ...")
        subprocess.run(["npm", "install"], cwd=str(lp), check=False)
    else:
        logger("Quartz уже существует — делаем git pull ...")
        git_pull(local_path)
    return "Quartz готов"

def copy_vault_to_quartz_content(vault_path: str, quartz_root: str, logger=print):
    """
    Копирует .md (и только .md) из vault в quartz_root/content/,
    сохраняя подпапки. Исключает .obsidian и .trash.
    """
    vault = Path(vault_path)
    target_content = Path(quartz_root) / "content"
    if target_content.exists():
        logger(f"Очищаем содержимое {target_content} (только md устаревшие файлы будут перезаписаны)")
        # не удаляем целиком, а будем перезаписывать/создавать
    else:
        target_content.mkdir(parents=True, exist_ok=True)

    excl = {".obsidian", ".trash", ".git"}
    copied = 0
    for md in vault.rglob("*.md"):
        # skip if any part in excluded
        if any(part in excl for part in md.parts):
            continue
        rel = md.relative_to(vault)
        dest = target_content / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(md, dest)
        copied += 1
    logger(f"Скопировано {copied} md файлов в {target_content}")
    return f"Синхронизировано {copied} файлов"

def run_quartz_build(quartz_root: str, logger=print):
    """
    Вызывает `npx quartz build` в quartz_root.
    Требует, чтобы `npx` и node/npm были установлены в системе.
    """
    qr = Path(quartz_root)
    if not qr.exists():
        raise FileNotFoundError("Quartz root не найден: " + quartz_root)
    
    # Проверяем доступность npx
    try:
        subprocess.run(["npx", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger("ОШИБКА: npx не найден в системе!")
        logger("Установите Node.js с официального сайта: https://nodejs.org/")
        logger("Или используйте GitHub режим деплоя вместо локального")
        raise RuntimeError("npx не найден. Установите Node.js или используйте GitHub режим")
    
    logger("Запуск сборки: npx quartz build ...")
    
    try:
        # Включаем вывод в real-time (stream)
        proc = subprocess.Popen(["npx", "quartz", "build"], cwd=str(qr),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # читаем поток и логируем
        for line in proc.stdout:
            logger(line.rstrip())
        proc.wait()
        
        if proc.returncode != 0:
            raise RuntimeError(f"quartz build завершился с кодом {proc.returncode}")
        
        logger("quartz build успешно завершён — проверьте папку public/")
        return "build ok"
        
    except Exception as e:
        logger(f"Ошибка при выполнении npx quartz build: {e}")
        raise RuntimeError(f"Ошибка сборки: {e}")
