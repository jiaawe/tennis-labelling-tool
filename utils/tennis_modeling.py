from enum import Enum

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

LH_COMBINATIONS = {
    'deuce': {
        'forehand': ['ii', 'io'],
        'backhand' : ['dl', 'cc']
    },
    'ad': {
        'forehand' : ['dl', 'cc'],
        'backhand' : ['ii', 'io']
    }
}

class GameState(Enum):
    START = 0
    RETURN = 1
    STROKE = 2
    SECOND_SERVE = 3

class ShotOutcome(Enum):
    IN = 0
    WIN = 1
    ERR = 2

def is_valid_transition(curr_state, next_state):
    '''
    This function checks whether the state transition is one that is allowed.
    '''    
    if curr_state == GameState.START and next_state == GameState.SECOND_SERVE:
        return True
    if curr_state == GameState.START and next_state != GameState.RETURN:
        return False
    if curr_state == GameState.RETURN and next_state == GameState.START:
        return False
    if curr_state == GameState.STROKE and next_state == GameState.START:
        return False
    # Need to handle first serve error
    return True

def get_state(shot, failed_first_serve):
    '''
    args: Player_Side_Court_Handedness_Shot_Direction_Formation_Outcome
    '''               
    # TEMPORARY FIX TO OBTAIN SECOND SERVE    
    if "serve" in shot and not failed_first_serve:        
        return GameState.START                
    if "serve" in shot:
        return GameState.SECOND_SERVE
    if "return" in shot:
        return GameState.RETURN    
    return GameState.STROKE

def get_outcome(outcome):
    '''
    This function gives us the outcome of that shot, to be used in determining
    whether to end the rally.
    '''
    if outcome == "in":
        return ShotOutcome.IN
    if outcome == "win":
        return ShotOutcome.WIN
    if outcome == "err":
        return ShotOutcome.ERR
    print("Invalid shot outcome detected")
    return None

def is_valid_shot(handedness, court, hand, shot, direction):
    '''
    This function checks through all handedness, court, hand, shot combinations
    and make sure they are valid according to tennis shot descriptions.
    '''        
    assert handedness in ['Right', 'Left']
    assert court in ['ad', 'deuce']
    assert hand in ['forehand', 'backhand']
    assert shot in ['serve', 'return', 'volley', 'volley', 'lob', 'smash', 'swing']
    assert direction in ['dl', 'cc', 'ii', 'io', 't', 'b', 'w'] 
    if shot == 'serve':
        return hand == 'forehand' and direction in ['t', 'b', 'w']
    if handedness == "Left":
        return direction in LH_COMBINATIONS[court][hand]
    return direction in RH_COMBINATIONS[court][hand]