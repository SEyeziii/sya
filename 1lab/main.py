import csv
import random
import math
from concurrent.futures import ProcessPoolExecutor


LETTERS = ['A', 'B', 'C', 'D']
N_FILES = 5
ROWS_PER_FILE = 20
SEED = 2025

random.seed(SEED)


def generate_csv_files():
    """Генерация 5 CSV файлов"""
    print("Генерация 5 CSV файлов...")
    for i in range(N_FILES):
        with open(f'data_{i}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Value'])
            for _ in range(ROWS_PER_FILE):
                category = random.choice(LETTERS)
                value = random.uniform(0, 100)
                writer.writerow([category, f"{value:.2f}"])
        print(f"  Создан файл: data_{i}.csv")


def process_single_file(filename):
    """Обработка одного файла: вычисление медианы и std для каждой категории"""
    # данные из файла
    data = {letter: [] for letter in LETTERS}

    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)

            for row in reader:
                if len(row) == 2:
                    category, value = row[0], float(row[1])
                    if category in data:
                        data[category].append(value)
    except Exception as e:
        print(f"Ошибка чтения файла {filename}: {e}")
        return {letter: {'median': None, 'std': None} for letter in LETTERS}

    # статистики для каждой категории
    result = {}
    for letter in LETTERS:
        values = data[letter]
        if values:

            sorted_values = sorted(values)
            n = len(sorted_values)

            if n % 2 == 1:
                median = sorted_values[n // 2]
            else:
                mid = n // 2
                median = (sorted_values[mid - 1] + sorted_values[mid]) / 2

            # стандартное отклонение
            if n > 1:
                mean = sum(values) / n
                variance = sum((x - mean) ** 2 for x in values) / (n - 1)
                std = math.sqrt(variance)
            else:
                std = 0.0

            result[letter] = {'median': median, 'std': std}
        else:
            result[letter] = {'median': None, 'std': None}

    return result


def main():
    generate_csv_files()

    print("\nПараллельная обработка файлов...")
    file_names = [f'data_{i}.csv' for i in range(N_FILES)]

    all_results = []
    with ProcessPoolExecutor() as executor:

        futures = [executor.submit(process_single_file, filename) for filename in file_names]

        for i, future in enumerate(futures):
            result = future.result()
            all_results.append(result)

            # промежуточные результаты
            print(f"\nФайл {i}:")
            for letter in LETTERS:
                median = result[letter]['median']
                std = result[letter]['std']
                median_str = f"{median:.2f}" if median is not None else "N/A"
                std_str = f"{std:.2f}" if std is not None else "N/A"
                print(f"  {letter}: медиана = {median_str}, отклонение = {std_str}")

    # все медианы по категориям
    print("\n" + "=" * 60)
    print("Сбор всех медиан по категориям...")
    print("=" * 60)

    all_medians_by_category = {letter: [] for letter in LETTERS}

    for file_result in all_results:
        for letter in LETTERS:
            median = file_result[letter]['median']
            if median is not None:
                all_medians_by_category[letter].append(median)

    print("\nСобранные медианы:")
    for letter in LETTERS:
        medians = all_medians_by_category[letter]
        print(f"  {letter}: {[round(m, 2) for m in medians]}")

    #  медиана медиан и отклонение медиан для каждой категории
    print("\n" + "=" * 60)
    print("ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 60)
    print(f"{'Категория':<10} {'Медиана медиан':<15} {'Отклонение медиан':<15}")
    print("-" * 40)

    final_results = []

    for letter in LETTERS:
        medians = all_medians_by_category[letter]

        if len(medians) > 0:
            # Сортируем медианы
            sorted_medians = sorted(medians)
            n = len(sorted_medians)

            # Медиана медиан
            if n % 2 == 1:
                median_of_medians = sorted_medians[n // 2]
            else:
                mid = n // 2
                median_of_medians = (sorted_medians[mid - 1] + sorted_medians[mid]) / 2

            # Стандартное отклонение медиан
            if len(medians) > 1:
                mean_of_medians = sum(medians) / len(medians)
                std_of_medians = math.sqrt(
                    sum((x - mean_of_medians) ** 2 for x in medians) / (len(medians) - 1)
                )
            else:
                std_of_medians = 0.0

            print(f"{letter:<10} {median_of_medians:<15.4f} {std_of_medians:<15.4f}")
            final_results.append([letter, median_of_medians, std_of_medians])
        else:
            print(f"{letter:<10} {'Нет данных':<15} {'Нет данных':<15}")
            final_results.append([letter, None, None])

    # сохранение результата в файл
    with open('final_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Category', 'Median_of_Medians', 'Std_of_Medians'])
        for row in final_results:
            if row[1] is not None:
                writer.writerow([row[0], f"{row[1]:.4f}", f"{row[2]:.4f}"])
            else:
                writer.writerow([row[0], 'N/A', 'N/A'])

    print("\n" + "=" * 60)
    print("Результаты сохранены в файл 'final_results.csv'")


    print("\nСодержимое файла final_results.csv:")
    with open('final_results.csv', 'r') as f:
        print(f.read())


if __name__ == "__main__":
    main()