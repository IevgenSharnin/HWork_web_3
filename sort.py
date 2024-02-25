# import sys
import shutil
from pathlib import Path
from normalize import normalize
from time import time
import logging
from threading import Thread, RLock

# словник з розширеннями файлів, що оброблюються
DICT_FOR_EXT = {'archives': ['ZIP', 'GZ', 'TAR'],
                'video': ['AVI', 'MP4', 'MOV', 'MKV'],
                'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
                'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
                'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
                'other': []}

#PATH = Path('D:/Crap') # вихідна папка для сортування
PATH = 0
threads = []
locker = RLock()
all_files = []
list_all_folders = []
suff_used_known = set ()
suff_used_unknown = set ()

# функція визначення типу файлу, виходячи зі словника
# визначає по розширенню файлу з крапкою перед ним ".ХХХ"
def filetype (suffix): 
    suffix = suffix.removeprefix ('.')
    for type, suffixes in DICT_FOR_EXT.items():
        for suff in suffixes:
            if suffix.lower() == suff.lower():
                 suff_used_known.add(suffix.upper())
                 return type
    suff_used_unknown.add(suffix.upper())
    return "other"

# функція власне сортування, параметр action - для другого прогону
# з нормалізацією та переміщенням
# перший прогон - тільки для інформації скільки і чого є 
def sorting (path_, action = False):
    for file in path_.iterdir(): #ім'я файлу з розширенням
        global threads, list_all_folders
        if file.is_dir():
            sorting (file, action) #рекурсуємо, якщо папка
        else:
            all_files.append (filetype (file.suffix)) # список усіх типів
# нормалізую ім'я файлу та переміщую у відповідну папку
            if action: 
                with locker: # на всяк випадок RLock, щоб два потоки не вхопили один файл
                    file_name_norm = f'{normalize (file.stem)}{file.suffix}'
                    file.replace (PATH / filetype (file.suffix) / file_name_norm)
# а тут розпаковую архів
                    if filetype (file.suffix) == 'archives':
                        shutil.unpack_archive (PATH / 'archives' / file_name_norm, 
                                               PATH / 'archives' / file.stem)
    return all_files

# Функція створення папок, в які розсортуємо, та видалення пустих:
# Працює, якщо відповідаємо 'у' після першого прогону.
# Аction 'new' створює, action 'del' видаляє 
def work_with_directories (path_: Path, action):
    global list_all_folders
    if action == 'new':
        for dir in path_.iterdir(): #ім'я папки нормалізую
            if dir.is_dir():
                dir.replace (PATH / normalize (dir.name))
                list_all_folders.append (PATH / normalize (dir.name))
        for dir_ in DICT_FOR_EXT.keys(): #створюю папки, якщо немає
            path_new_dir = path_ / dir_
            path_new_dir.mkdir (exist_ok = True, parents = True)
    if action == 'del':
        for dir in path_.iterdir():
            if dir.is_dir() and (dir.name not in DICT_FOR_EXT.keys()):
                try: 
                    dir.rmdir ()
                except OSError:
                    work_with_directories (dir, action = 'del')
                    work_with_directories (PATH, action = 'del')
#                    logging.error ('Велика вкладеність папок. Запусти програму ще раз')

# початок роботи програми - пишемо в консоль и виклик функції
def run():
    while True:
        dir = input ('Введіть шлях до папки для сортування: ')
        global PATH
        PATH = Path(dir)
        if PATH.exists():
            break
        else:
            print ('Введений шлях не існує. Спробуйте ще раз') 

    first = time ()
    sorting (PATH)

#вивід результатів першого прогону
    second = time()
    print (f'\nВміст папки: {PATH}')
    print ('|{:-^15}|{:-^10}|'.format ('-', '-'))
    print ('|{:^15}|{:^10}|'.format ('Типи файлів', 'Кількість'))
    print ('|{:-^15}|{:-^10}|'.format ('-', '-'))
    print ('|{:<15}|{:^10}|'.format ('Зображення', all_files.count('images')))
    print ('|{:<15}|{:^10}|'.format ('Відео', all_files.count('video')))
    print ('|{:<15}|{:^10}|'.format ('Документи', all_files.count('documents')))
    print ('|{:<15}|{:^10}|'.format ('Музика', all_files.count('audio')))
    print ('|{:<15}|{:^10}|'.format ('Архіви', all_files.count('archives')))
    print ('|{:<15}|{:^10}|'.format ('Інші типи', all_files.count('other')))
    print ('|{:-^15}|{:-^10}|'.format ('-', '-'))
    print ('|{:<15}|{:^10}|'.format ('Разом', len (all_files)))
    print ('')
    print (f'Час роботи: {round(second - first, 3)} сек')
    print ('')
    global suff_used_known 
    if suff_used_known == set():
        suff_used_known = "Не знайдено"
    print (f'Знайдено наступні відомі типи файлів: {suff_used_known}')
    global suff_used_unknown 
    if suff_used_unknown == set():
        suff_used_unknown = "Не знайдено"
    print (f'Знайдено наступні невідомі типи файлів ("Інші типи"): {suff_used_unknown}')
    print ('')
    yn = input ('Продовжити виконання завдання: перейменування файлів за \
допомогою транслітерації та їх переміщення у папки за типами \
(y - yes / n - no): ')
    print ('')
    while True:
        if yn not in 'yn':
            yn = input("Будь ласка, введіть 'y' або 'n': ") 
        else: break
    if yn == 'n':
        print ('Дякую за увагу!\n')
    else:
        work_with_directories (PATH, 'new') # створюємо цільові папки

# Блок з багатопоточністю - нормалізуємо та переміщуємо файли згідно списку нормалізованих папок
        global threads
        list_all_folders.append (PATH)
        for folder in list_all_folders:
            th = Thread (target = sorting, args = (folder,True))
            th.start()
            threads.append(th)
        [th.join() for th in threads]

#        sorting (PATH, action = True) # нормалізуємо та переміщуємо файли - версія без багатопотоків
        work_with_directories (PATH, 'del') # видаляємо усі пусті папки
        print ('Імена файлів нормалізовані. Файли перемещені у\
 відповідні папки.\n')
        
if __name__ == '__main__':
    logging.basicConfig (level=logging.INFO, format="%(threadName)s %(message)s")
    run()
