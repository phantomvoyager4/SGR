import json

game_chunk = 1
file_path = f"data/games_prices/price_data_chunk_{game_chunk}.jsonl"

validation_flag = 1
empty_lists = 0
data_errors = 0
correct_answers = 0
last_id = 0
game_ids = []

try:
    with open(file_path, "r", encoding="utf-8") as jsonl_file:
        for line_num, line in enumerate(jsonl_file, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                line_data = json.loads(line)
                
                if not line_data:
                    print(f'Missing line {line_num}')
                    continue
                    
                game_id_str, history_data = list(line_data.items())[0]
                game_id = int(game_id_str)

                if(game_id in game_ids):
                    print(f'duplicated id {game_id}')
                    validation_flag = 0
                game_ids.append(game_id)
                
                if history_data == "Data_error":
                    data_errors += 1
                    #print(f"Line {line_num}: Data_error for ID {game_id}")
                    continue 

                elif isinstance(history_data, list) and len(history_data) == 0:
                    empty_lists += 1
                else:
                    correct_answers += 1

                if line_num > 1 and last_id != 0:
                    if game_id < last_id:
                        print(f'Game ID decreased on line {line_num} for ID {game_id}, after {last_id}')
                    elif game_id == last_id:
                        print(f'Duplicated ID found on line {line_num}: {game_id}')
                        validation_flag = 0
                
                last_id = game_id
                            
            except json.JSONDecodeError:
                print(f"Skipping malformed JSON syntax on line {line_num}.")
                data_errors += 1
                
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")

if(validation_flag):
    print('Validation Complete')
else:
    print('Validation failed')
print(f'Number of games with empty history: {empty_lists}')
print(f'Number of games with data errors:    {data_errors}')
print(f'Number of games fetched correctly:  {correct_answers}')
print(f'Sum of records {empty_lists + data_errors + correct_answers}')