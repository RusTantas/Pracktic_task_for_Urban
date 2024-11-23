import os
import pandas as pd


class PriceMachine:
    def __init__(self):
        self.data = []
        self.name_length = 0

    def load_prices(self, file_path="data"):
        """Загружает данные из всех прайс-листов в указанной директории."""
        # Получаем абсолютный путь к папке data
        base_path = os.path.dirname(os.path.abspath(__file__))  # Путь к текущей директории
        data_path = os.path.join(base_path, file_path)  # Полный путь к папке data

        for file_ in os.listdir(data_path):
            if "price" in file_ and file_.endswith(".csv"):
                file_path_full = os.path.join(data_path, file_)
                try:
                    # Загружаем данные, разделенные запятой
                    df = pd.read_csv(file_path_full, sep=',', encoding="utf-8")
                    if df.empty:
                        print(f"Файл {file_} пуст.")
                        continue

                    # Определяем названия столбцов
                    name_col = self._find_column(df.columns, ["название", "товар", "наименование", "продукт"])
                    price_col = self._find_column(df.columns, ["цена", "розница"])
                    weight_col = self._find_column(df.columns, ["вес", "фасовка", "масса"])

                    if name_col and price_col and weight_col:
                        df_selected = df[[name_col, price_col, weight_col]].copy()
                        df_selected.columns = ["name", "price", "weight"]

                        # Преобразуем цену и вес в числовые типы
                        df_selected["price"] = pd.to_numeric(df_selected["price"], errors='coerce')
                        df_selected["weight"] = pd.to_numeric(df_selected["weight"], errors='coerce')

                        # Удаляем строки с NaN в цене или весе
                        df_selected.dropna(subset=["price", "weight"], inplace=True)

                        if not df_selected.empty:
                            df_selected["file"] = file_
                            df_selected["price_per_kg"] = df_selected["price"] / df_selected["weight"]
                            self.data.append(df_selected)
                            print(f"Данные из файла {file_} успешно загружены.")
                        else:
                            print(f"Все строки в {file_} были удалены из-за NaN значений.")
                    else:
                        print(f"Не удалось найти необходимые столбцы в {file_}.")
                except Exception as e:
                    print(f"Ошибка при чтении файла {file_}: {e}")

    def _find_column(self, columns, variants):
        """Находит первый столбец из списка вариантов."""
        for variant in variants:
            if variant in columns:
                return variant
        return None

    def export_to_html(self, fname="output.html"):
        """Экспортирует собранные данные в HTML-файл."""
        if not self.data:
            print("Нет данных для экспорта.")
            return

        all_data = pd.concat(self.data, ignore_index=True)

        # Сортируем данные по цене за килограмм перед экспортом
        all_data.sort_values(by="price_per_kg", inplace=True)

        html_content = """
        <html>
        <head>
            <title>Цены</title>
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                }
                th {
                    background-color: #f2f2f2;
                }
            </style>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        """

        for idx, row in all_data.iterrows():
            html_content += f"""
                <tr>
                    <td>{idx + 1}</td>
                    <td>{row['name']}</td>
                    <td>{row['price']}</td>
                    <td>{row['weight']}</td>
                    <td>{row['file']}</td>
                    <td>{row['price_per_kg']:.2f}</td>
                </tr>
            """

        html_content += """
            </table>
        </body>
        </html>
        """

        with open(fname, "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Данные успешно выгружены в output.html.")

    def find_text(self, search_text: str) -> pd.DataFrame:
        """Поиск в загруженных данных по названию товара."""
        all_data = pd.concat(self.data, ignore_index=True)

        filtered_data = all_data[
            all_data["name"].str.contains(search_text.strip(), case=False, na=False)
        ]

        # Сортируем отфильтрованные данные по цене за килограмм
        filtered_data.sort_values(by="price_per_kg", inplace=True)

        if filtered_data.empty:
            return "Данных с таким значением не существует."

        return filtered_data


# Пример использования класса PriceMachine
if __name__ == "__main__":
    price_machine = PriceMachine()

    # Загрузка данных из прайс-листов
    price_machine.load_prices()

    # Экспорт загруженных данных в HTML
    price_machine.export_to_html(fname="output.html")

    # Циклический интерфейс для поиска товаров
    while True:
        input_ = input("Поиск (введите 'exit' для выхода): ").strip()

        if input_.lower() == "exit":
            print("Работа завершена.")
            break

        result = price_machine.find_text(input_)

        if isinstance(result, str):
            print(result)  # Сообщение об отсутствии данных
        else:
            print(result.to_string(index=False))  # Вывод найденных позиций при наличии данных