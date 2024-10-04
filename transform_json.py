from copy import deepcopy
from enum import Enum
from random import randint
import argparse
import json
import random

random.seed(42)

RH_COMBINATIONS = {
    'deuce': {
        'forehand': ['dl', 'cc'],
        'backhand' : ['ii', 'io']
    },
    'ad': {
        'forehand' : ['ii', 'io'],
        'backhand' : ['dl', 'cc']
    }
}
TEMPLATE = {
    "video_id": None,
    "num_frames": None,
    "events":[]
} 

RANDOM_START = [10, 21]
RANDOM_END = [30, 51]

class GameState(Enum):
    START = 0
    RETURN = 1
    STROKE = 2
    END = 3


def main(files):
    filepath = './data/labelled/'    
    jsons = []
    for file in files:              
        with open(f'{filepath}{file}', 'r') as f:                        
            jsons += f.read().splitlines()
            f.close()    
    for json_file in jsons:             
        filename = json_file.split(".")[0]  
        with open(f'{filepath}{json_file}', 'r') as json_data:
            d = json.load(json_data)  
            json_data.close()            
            new_json_data = process(d)
        with open(f'{filepath}{filename}_transformed.json', 'w') as f:
            json.dump(new_json_data, f, indent=2)

def get_state(shot, outcome):
    '''
    args: Player_Side_Court_Handedness_Shot_Direction_Formation_Outcome
    '''            
    if "serve" in shot:
        return GameState.START
    if "return" in shot:
        return GameState.RETURN
    if "win" in outcome or "err" in outcome:
        return GameState.END        
    return GameState.STROKE

def get_start_frame(frame):
    random_start = randint(RANDOM_START[0], RANDOM_START[1])
    return max(0, frame - random_start)

def get_end_frame(frame, total_frames):    
    random_end = randint(RANDOM_END[0], RANDOM_END[1])
    return min(total_frames, frame + random_end)

def handle_start(label, rally):
    '''
    This function takes in the empty json template, updates the start frame 
    in the video id, and adds the current event.
    '''                
    current_frame = label['frame']
    start_frame = get_start_frame(current_frame)
    rally['video_id'] += f'_{start_frame}'    
    rally['num_frames'] = start_frame
    label['frame'] = current_frame - start_frame
    rally['events'].append(label)

def handle_normal(label, rally):
    label['frame'] -= rally['num_frames']
    rally['events'].append(label)

def handle_end(label, rally, total_frames):            
    assert(rally['num_frames'])  
    start_frame = rally['num_frames']  
    end_frame = get_end_frame(label['frame'], total_frames)
    label['frame'] -= start_frame
    rally['num_frames'] = end_frame - start_frame
    rally['video_id'] += f'_{end_frame}'    
    rally['events'].append(label)

def process(json_data):    
    TOTAL_FRAMES = json_data['total_frames'] 
    TEMPLATE['video_id'] = json_data['video_id']    
    body = json_data['events']    
    result = {
        "video_id": json_data['video_id'],
        "fps": json_data["fps"],
        "player_descriptons": json_data['player_descriptions']
    }

    rallies = []
    current_rally = deepcopy(TEMPLATE)    
    for label in body:        
        args = label['event'].split('_')
        _, _, court, hand, shot, direction, _, outcome = args
        state = get_state(shot, outcome)   
        if state != GameState.START and direction not in RH_COMBINATIONS[court][hand]:
            print(f"frame {label['frame']} Wrong Label")
            # return None             
        if state == GameState.START:
            handle_start(label, current_rally)                                  
        elif state == GameState.RETURN or state == GameState.STROKE:
            handle_normal(label, current_rally)        
        elif state == GameState.END:
            handle_end(label, current_rally, TOTAL_FRAMES)
            rallies.append(current_rally)            
            current_rally = deepcopy(TEMPLATE)   
        else: # added to ensure all cases are covered
            print(f"frame {label['frame']} Wrong Label")
            return None   
        result['rallies'] = rallies      
    return result
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add your files')
    parser.add_argument("-f", "--files", nargs='+', default=[])
    args = parser.parse_args()    
    main(args.files)
