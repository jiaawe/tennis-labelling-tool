from copy import deepcopy
from enum import Enum
from random import randint
import argparse
import json
import random
import os 

from utils.tennis_modeling import GameState, ShotOutcome, get_outcome, \
    get_state, is_valid_transition, is_valid_shot, assign_player_sides, is_valid_second_serve

random.seed(42)

TEMPLATE = {
    "video_id": None,
    "num_frames": None,
    "events":[]
}

RANDOM_START = [10, 21]
RANDOM_END = [30, 51]

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

# TEMP FUNCTION
def handle_second_serve(label, rally):
    args = label['event'].split('_')
    args[4] = 'second-serve'
    label['event'] = ('_').join(args)
    label['frame'] -= rally['num_frames']
    rally['events'].append(label)


def handle_end(label, rally, total_frames):            
    assert('num_frames' in rally)  
    start_frame = rally['num_frames']  
    num_frames = get_end_frame(label['frame'], total_frames)         
    end_frame = start_frame + num_frames    
    rally['num_frames'] = num_frames
    rally['video_id'] += f'_{end_frame}'        

def main(files):
    filepath = './data/labelled/'
    savepath = './data/transformed/'
    os.makedirs(savepath, exist_ok=True)
    jsons = []
    
    for file in files:
        file_path = os.path.join(filepath, file.strip())
        with open(file_path, 'r') as f:
            jsons.extend([line.strip() for line in f])
    
    for json_file in jsons:
        filename = json_file.split(".")[0]
        json_file_path = os.path.join(filepath, json_file)
        
        with open(json_file_path, 'r') as json_data:
            d = json.load(json_data)
        
        new_json_data = process(d)
        
        save_file_path = os.path.join(savepath, f"{filename}_transformed.json")
        with open(save_file_path, 'w') as f:
            json.dump(new_json_data, f, indent=2)

def process(json_data):    
    TOTAL_FRAMES = json_data['total_frames'] 
    TEMPLATE['video_id'] = json_data['video_id']    
    body = json_data['events']    
    result = {
        "video_id": json_data['video_id'],
        "fps": json_data["fps"],
        "player_descriptons": json_data['player_descriptions'],
        "player_hands": json_data['player_hands']
    }

    print(f"Currently processing {json_data['video_id']}")
    # Initialize variables that will be modified each rally
    rallies = []
    current_rally = deepcopy(TEMPLATE)    
    prev_state = None
    prev_side= None
    player_sides = None
    failed_one_serve, failed_serve_label = False, None
    
    started = False
    for label in body:        
        args = label['event'].split('_')
        player, side, court, hand, shot, direction, _, outcome = args
        handedness = json_data["player_hands"][player.lower()]
        state, outcome = get_state(shot, failed_one_serve), get_outcome(outcome)        

        if not is_valid_shot(handedness, court, hand, shot, direction):
            print(f"Frame {label['frame']}: Invalid shot combination.")
            return None
        
        if state == GameState.START:  
            started = True
            if outcome == ShotOutcome.ERR:                
                failed_one_serve = True          
                failed_serve_label = [player, side, court, hand]
            prev_state = state
            prev_side = side
            player_sides = assign_player_sides(player, side)
            handle_start(label, current_rally)
            if outcome == ShotOutcome.WIN:    
                started = False            
                handle_end(label, current_rally, TOTAL_FRAMES)            
                rallies.append(current_rally)                        
                current_rally = deepcopy(TEMPLATE)   
            continue                                               

        if not started:
            print(f"Frame {label['frame']}: Invalid shot type. Rally must start with Serve")
            return None
        
        if not is_valid_transition(prev_state, state):
            print(f"Frame {label['frame']}: Invalid state transition")
            return None
        
        if side == prev_side and state != GameState.SECOND_SERVE:
            print(f"Frame {label['frame']}: Invalid side label")
            return None
        
        if state == GameState.SECOND_SERVE:
            assert failed_one_serve and failed_serve_label            
            if not is_valid_second_serve(failed_serve_label, player, side, court, hand):
                print(f"Frame {label['frame']}: Invalid second serve")
                return None
        if player not in player_sides[side]:
            print(f"Frame {label['frame']}: Invalid player detected at indicated side for frame")         

        # Side, player and state transitions are all valid
        prev_state, prev_side = state, side
        
        if state == GameState.SECOND_SERVE:
            failed_one_serve = False   
            failed_serve_label = None                     
            handle_second_serve(label, current_rally)
        else:
            handle_normal(label, current_rally)        
        
        if outcome == ShotOutcome.WIN or outcome == ShotOutcome.ERR:
            started = False
            handle_end(label, current_rally, TOTAL_FRAMES)            
            rallies.append(current_rally)                        
            current_rally = deepcopy(TEMPLATE)   
        
    result['rallies'] = rallies      
    return result
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add your files')
    parser.add_argument("-f", "--files", nargs='+', default=[])
    args = parser.parse_args()    
    main(args.files)
