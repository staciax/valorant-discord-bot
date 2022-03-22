# Standard
import json

# data_store
def data_read(filename):
    with open("data/" + filename + ".json", "r", encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

def data_save(filename, data):
    with open("data/" + filename + ".json", 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)

def config_read():
    with open("settings.json", "r", encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

def config_save(data):
    with open("settings.json", 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)