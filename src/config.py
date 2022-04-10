import _thread as _thread
import time

#preset mode class
class preset_mode:
    def __init__(self, mode, start_time, end_time):
        
        if mode in possible_config['mode']:
            self.mode = mode
        else:
            raise Exception('Tried to write invalid mode')
        if not (isinstance(start_time, time.struct_time) and isinstance(end_time, time.struct_time)):
            raise Exception('Times entered are not in struct_time form')
        else:
            self.start_time = start_time
            self.end_time = end_time
            print ('All variables initialised')
            
# define configuration parameters and the values they can take
possible_config = {
        'mode'              : ('active', 'secure', 'off', 'aggressive' ),
        'status'            : ('closed', 'opening', 'open_left', 'open_right', 'closing', 'obstruction'),
        'position'          : ('closed', 'open_left', 'open_right'),
        'on_fire'           : (True, False),
        'adult_there_left'  : (True, False),
        'adult_there_right' : (True, False),
        'open_angle_right'  : None,
        'open_angle_left'   : None,
        'preset_mode'       : None,
        'stay_open_time'    : None
        }

# initialise empty arrays for the opening/closing time lists
config = {
        'preset_mode'  : []
        }

# tracks thread ending for safe termination
thread_end = {
    'alarm'         : (True, False),
    'gate_control'  : (True, False),
    'vision'        : (True, False)
}

config_lock = _thread.allocate_lock()

def can_run(thread):
    if thread in thread_end:
        return thread_end[thread]
    else:
        raise Exception('Thread does not exist or cannot be terminated')

def set_to_end(thread):
    if thread in thread_end:
        thread_end[thread] = False
    else:
        raise Exception('Thread cannot be terminated')

def set_to_start(thread):
    if thread in thread_end:
        thread_end[thread] = True
    else:
        raise Exception('No such thread!')

def write_config(parameter, value):
    config_lock.acquire(True)
    if parameter in possible_config:
        if possible_config[parameter] is None:
            config[parameter] = value
        elif value in possible_config[parameter]:
            config[parameter] = value
        else:
            config_lock.release()
            raise Exception('Tried to write invalid config value')
    else:
        config_lock.release()
        raise Exception('Tried to write to invalid config parameter')
    config_lock.release()

def read_config(parameter):
    config_lock.acquire(True)
    if parameter in config:
        return_value = config[parameter]

    if parameter in config:
        config_lock.release()
        return return_value
    else:
        config_lock.release()
        raise Exception('Tried to read non-existant config parameter')

# for deleting elements in the opening/closing time arrays
def delete_preset_modes():
    config_lock.acquire(True)
    config['preset_mode']=list()
    config_lock.release()


def write_preset_mode(parameter):
    config_lock.acquire(True)
    if isinstance(parameter, preset_mode):
        config['preset_mode'].append(parameter)
    else:
        raise Exception('Invalid preset mode')
    config_lock.release()

# write default config
write_config('mode',                'active')
write_config('status',              'closed')
write_config('position',            'closed')
write_config('on_fire',             False)
write_config('adult_there_left',    False)
write_config('adult_there_right',   False)
write_config('open_angle_right',    90)
write_config('open_angle_left',     90)
write_config('stay_open_time',      5)

# Self test module
if __name__ == "__main__":
    write_config('mode', 'secure')
    assert read_config('mode') == 'secure'
    print('Test passed')
