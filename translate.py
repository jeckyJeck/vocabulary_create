from google.cloud import translate_v2 as translate
import json

client = translate.Client()

not_exist = []

word_list_path = r"\word_lists\word_list.txt"
english_output_path = r"\output"
start = 0
end = 5000
output_file = r"\hebrew_output"
with open(word_list_path, 'r') as file:
    counter = start + 1
    file = file.readlines()[start:end]
    for line in file:
        file_number = (counter // 500) + 1
        counter += 1
        line = line.strip()
        if len(line) < 3:
            continue
        path = fr"{english_output_path}\output{file_number}\{line}.json"
        try:
            with open(path, 'r') as f:
                # load the json file into batch and translate it
                batch = []
                word_data = json.load(f)
                # check the json structure
                if 'word' not in word_data or 'main_definition' not in word_data or 'meanings_and_examples' not in word_data:
                    print(f"{line} file does not have the correct structure")
                    not_exist.append(line + f"{line} file does not have the correct structure")
                    continue
                batch.append(line)
                main_definition = word_data['main_definition']
                batch.append(main_definition)
                meanings = word_data['meanings_and_examples']
                new_meanings = []
                for meaning in meanings:
                    if 'definition' not in meaning or 'example' not in meaning:
                        print(f"{line} file does not have the correct structure")
                        not_exist.append(line + f"{line} file does not have the correct structure")
                        continue
                    try:
                        definition = meaning['definition']
                        example = meaning['example']
                        batch.append(definition)
                        batch.append(example)
                    except: 
                        print(f"{line} file does not have the correct structure")
                        not_exist.append(line + f"{line} file does not have the correct structure")

                try:
                    hebrew_batch = client.translate(batch, target_language="iw", source_language="en", format_="text")
                except Exception as e:
                    print(f"Could not translate {line} because of the following error: {e}")
                    not_exist.append(line + f"Could not translate {line} because of the following error: {e}")
                    continue
                # check if the translation was successful
                if hebrew_batch == None or len(hebrew_batch) < 4:
                    not_exist.append(line)
                    continue
                # create translated json
                new_meanings = []
                for i in range(2, len(hebrew_batch), 2):
                    new_meanings.append({"definition": batch[i],
                                         "definition_hebrew": hebrew_batch[i]['translatedText'],
                                         "example": batch[i+1],
                                         "example_hebrew": hebrew_batch[i+1]['translatedText']})    
                word_json = {"word": line,
                                  "word_hebrew": hebrew_batch[0]['translatedText'], 
                                 "main_definition": main_definition,
                                   "main_definition_hebrew": hebrew_batch[1]['translatedText'],
                                     "meanings_and_examples": new_meanings}
                with open(f"{output_file}/{line}.json", 'w', encoding='utf-8') as f:
                    json.dump(word_json, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            print(f"{line} file does not exist")
            not_exist.append(line + f"{line} file does not exist")
            continue
        print(line)
        
with open(f"{output_file}/not_exist.txt", 'a') as f:
    f.write("\n".join(not_exist))