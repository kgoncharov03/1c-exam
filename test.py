import myers

# Пример запуска
# Получение различий в файл, указанный 3 аргументом
myers.get_small_diff_file('first.bin', 'second.bin', 'diff.bin')

# Обновление файла в файл, указанный 3 аргументом
myers.patch_file_with_small_diff('first.bin', 'diff.bin', 'result.bin')