import genanki
import json

def base_model():
    all_fields = [{'name': 'word'},
            {'name': 'word_hebrew'},
            {'name': 'main_definition'},
            {'name': 'main_definition_hebrew'}]
    for i in range(1, num_of_definitioins+1):
        all_fields.append({'name': f'definition{i}'})
        all_fields.append({'name': f'definition{i}_hebrew'})
        all_fields.append({'name': f'example{i}'})
        all_fields.append({'name': f'example{i}_hebrew'})
    definitions_rect_html = ""
    for i in range(1, num_of_definitioins+1):
        definitions_rect_html += f"""<div class="definition-rect">
        <p class="definition">{{{{definition{i}}}}}</p>
                            <p class="definition-hebrew">{{{{definition{i}_hebrew}}}}</p>
                            <p class="example">{{{{example{i}}}}}</p>
                            <p class="example-hebrew">{{{{example{i}_hebrew}}}}</p>
                            </div>"""
        
    return genanki.Model(
        12131415,
        'Simple Model',
        fields=all_fields,
        templates=[
        {
            'name': 'Card 1',
            'qfmt': '''<p class="head" style="text-align: center; font-size: 18px">{{word}}</p>
            <details>
            <summary>example:</summary>
            <p class="details-example head">{{example1}}</p>
            </details>
            ''',
            'afmt': """
                    <p class="head" style="text-align: center; font-size: 18px">{{word}}</p><hr id="answer">
                    <p class="head" style="text-align: center; font-size: 18px; direction: rtl;">{{word_hebrew}}</p>
                    <p class="head" style="text-align: center; font-size: 18px">{{main_definition}}</p>
                    <p class="head" style="text-align: center; font-size: 18px; direction: rtl;">{{main_definition_hebrew}}</p>
                    <div class="definition-slider">
                        """+f"{definitions_rect_html}" +"""
                    </div>    
                    <a style="text-align: center;" href="https://translate.google.co.il/?hl=iw&sl=en&tl=iw&text={{word}}&op=translate">Google Translate</a>
                    """,
        },
    ],
    css="""
       body {
        background-color: #e8e8e8;
        color: black;
        }
        .definition-slider {
        display: flex;
        overflow-x: scroll;
        white-space: nowrap; /* Prevent wrapping */
        }

        .definition-rect {
        flex: 0 0 auto; 
        margin-right: 10px; /* Add spacing between rectangles */
        border-radius: 8px;
        background-color: #ffffff; /* Light background color */
        }

        p:empty {
            display: none; /* Hide empty paragraphs */
        }
        p {
        padding-left: 10px; /* Add padding */
        padding-right: 10px; /* Add padding */
        width: 200px; /* Set width */
        white-space: pre-wrap; /* Allow line wrapping */
        }
        p.head {
        width: 100%;
        }
        p.definition {
        font-size: 16px;
        font-weight: bold; /* Bold text */
        
        }
        p.definition-hebrew {
        font-size: 14px;
        direction: rtl; /* Right-to-left text */
        font-style: italic; /* Italic text */
        }
        p.example {
        font-size: 16px;
        }
        p.example-hebrew {
        font-style: italic; /* Italic text */
        direction: rtl; /* Right-to-left text */
        }
    """
    )

def create_note(model, fields):
    # if the fields are less than the number of definitions*4+4, add empty strings
    if len(fields) < num_of_definitioins*4+4:
        for i in range(len(fields), num_of_definitioins*4+4):
            fields.append("")
    return genanki.Note(
        model=model,
        fields=fields
    )



word_list_path = r"\word_lists\word_list.txt"
output_file = r"\decks"
start = 8000
end = 10000
num_of_definitioins = 10

model = base_model()
deck = genanki.Deck(2050, f"english vocabulary {start}-{end}")
unfounds = []


with open(word_list_path, 'r') as file:
    file = file.readlines()[start:end]
    for line in file:
        line = line.strip()
        if len(line) < 3:  
            continue
        path = fr"{output_file}\{line}.json"
        try:
            with open(path, 'r', encoding='utf-8') as f:
                word_data = json.load(f)
                if isinstance(word_data, list):
                    word_data = word_data[0]
                fields = [line, word_data['word_hebrew'], word_data['main_definition'], word_data['main_definition_hebrew']]
                for meaning in word_data['meanings_and_examples']:
                    fields.append(meaning['definition'])
                    fields.append(meaning['definition_hebrew'])
                    fields.append('"' + meaning['example'] + '"')
                    fields.append('"' + meaning['example_hebrew'] + '"')
                if len(fields) > num_of_definitioins*4+4:
                    fields = fields[:num_of_definitioins*4+4]
                note = create_note(model, fields)
                deck.add_note(note)
        except FileNotFoundError:
            unfounds.append(line)
            print(f"{line} file does not exist")
            continue
        print(line)
    # save the deck
    genanki.Package(deck).write_to_file(f"{output_file}/deck{start}-{end}.apkg")
    with open(f"{output_file}/unfounds{start}-{end}.txt", 'w') as f:
        for item in unfounds:
            f.write("%s\n" % item)



