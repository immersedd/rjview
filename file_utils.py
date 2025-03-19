import os
import json
import pickle
from os.path import join
from typing import Any, List


def load_json(directory: str, filename: str) -> Any:
    file_path = os.path.join(directory, filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def dump_json(directory: str, filename: str, data: Any) -> None:
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_pickle(directory: str, filename: str) -> Any:
    file_path = os.path.join(directory, filename)
    with open(file_path, 'rb') as file:
        return pickle.load(file)


def dump_pickle(directory: str, filename: str, data: Any) -> None:
    file_path = os.path.join(directory, filename)
    with open(file_path, 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)


def get_sql_text(sql_file: str) -> str:
    with open(sql_file, 'r', encoding='utf-8') as file:
        return file.read()


def save_text_to_file(filepath: str, content: str) -> None:
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)


def get_files_by_extension(directory: str, extension: str = '.json') -> List[str]:
    return [filename for filename in os.listdir(directory) if filename.endswith(extension)]