from ollama import generate
import csv
import requests
import json


def get_json_from_phi3(word):
    prompt = f'''define in simple English all the meanings of the word\idiom "{word}", and provide example for each meaning.
    in addition, write the most useful and comperhensive definition as the main definition. 
    answer in JSON format as follows, with no other fields:
        {{
            "word": "{word}",
            "main_definition": "<main_definition>",
            "meanings_and_examples": [
            {{
            "definition": "<defintion1>",
            "example": "<example1>"
            }},
        ]
        }}
        and so on for each meaning.
    '''
    
    # Generate the response
    response = generate('phi3', prompt, format='json')
    json_response = json.loads(response['response'])

    return json_response

def get_examlpe_from_phi3(word, definition):
    prompt = f'''provide short example for the word\idiom "{word}" with the meaning "{definition}".
    answer in JSON format as follows:
        {{
            "word": "{word}",
            "definition": "{definition}",
            "example": "<example>"
        }}
    '''
    # process the response and take out the example
    response = generate('phi3', prompt, format='json')
    json_response = json.loads(response['response'])
    example = json_response['example']
    return example

def get_from_free_dictionary(word):
    final_json = {"word": word,
                "main_definition": "",
                "meanings_and_examples": []
    }
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    json_response = response.json()
    meanings = json_response[0]['meanings']
    for meaning in meanings:
        definitions = meaning['definitions']
        for definition in definitions:
            if 'example' not in definition:
                print("Getting example from phi3 for the word:", word)
                definition['example'] = get_examlpe_from_phi3(word, definition['definition'])
            json_definition = {"definition": definition['definition'],
                               "example": definition['example']}
            final_json["meanings_and_examples"].append(json_definition)
        
    final_json["main_definition"] = final_json["meanings_and_examples"][0]["definition"]
    
    return final_json

def write_to_file(json_to_write, name, counter):
    with open(f'output/output{counter}/{name}.json', 'w') as f:
        json.dump(json_to_write, f)

for i in range(21, 26):
    with open(f'word_lists/word_list{i}.txt', 'r') as f:
        words = f.readlines()
        for word in words:
            word = word.strip()
            if len(word) < 3:
                continue
            try:
                wanted_json = get_json_from_phi3(word)
                # wanted_json = get_from_free_dictionary(word)
                # if wanted_json is None:
                #     print(f"Could not find '{word}' in the free dictionary. Trying phi3...")
                #     wanted_json = get_json_from_phi3(word)
                
                write_to_file(wanted_json, word, i)
                print(word)
            except Exception as e:
                print(f"An error occurred while processing '{word}': {str(e)}")
        
