import time

from dragonfly import *

from lib import utilities

def navigate_to_character(direction3, target):
    # to do: possibly speed up the keypresses by figuring out how many lines up or down to go first
    try:
        left_or_right = str(direction3)
        look_left = left_or_right == "left"
        is_character = str(target) in [".", ",", "(~)", "[~]", "{~}", "(", ")", "(~[~{", "}~]~)"]
        
        # make sure nothing is highlighted to boot
        Key("right, left" if look_left else "left, right")._execute()
        
        max_highlights = 100
        index = -1
        last_copy_was_successful = True
        context = None
        for i in range(0, max_highlights):
            if last_copy_was_successful:
                if look_left:
                    Key("cs-left")._execute()
                else:
                    Key("cs-right")._execute()
                # reset success indicator
                last_copy_was_successful = True
            results = read_selected_without_altering_clipboard()
            error_code = results[0] 
            if error_code == 1:
                continue
            if error_code == 2:
                last_copy_was_successful = False
                continue
            context = results[1]
            
            index = find_index_in_context(target, context, look_left)
            if index != -1:
                break
        
        # highlight only the target
        if index != -1:
            Key("left" if look_left else "right")._execute()
            nt = index if look_left else len(context) - index - 1  # number of times to press left or right before the highlight
            if nt != 0:
                Key("right/5:" + str(nt) if look_left else "left/5:" + str(nt))._execute()
            if is_character:
                Key("s-right" if look_left else "s-left")._execute()
            else:
                Key("cs-right" if look_left else "cs-left")._execute()
        else:
            # reset cursor
            Key("left" if not look_left else "right")._execute()
            
    except Exception:
        utilities.simple_log(False)

def find_index_in_context(target, context, look_left):
    tlist = target.split("~")
    index = -1
    if look_left:
        index = -99999
        for t in tlist:
            tmpindex = context.rfind(t)  #
            if tmpindex != -1 and tmpindex > index:  # when looking left, we want the largest index
                index = tmpindex
    else:
        index = 99999  # arbitrarily large number
        for t in tlist:
            tmpindex = context.find(t)
            if tmpindex != -1 and tmpindex < index:  # conversely, when looking right, we want the smallest index
                index = tmpindex
    if index == 99999 or index == -99999:
        return -1
    return index

def read_selected_without_altering_clipboard(same_is_okay=False):
    '''Returns a tuple:
    (0, "text from system") - indicates success
    (1, None) - indicates no change
    (2, None) - indicates clipboard error, should not advance cursor before trying again
    '''
    time.sleep(0.05)  # time for previous keypress to execute
    cb = Clipboard(from_system=True)
    temporary = None
    prior_content = None
    try: 

        prior_content = Clipboard.get_system_text()
        Clipboard.set_system_text("")
    
        Key("c-c")._execute()
        time.sleep(0.05)  # time for keypress to execute
        temporary = Clipboard.get_system_text()
        cb.copy_to_system()

        
    except Exception:
        utilities.simple_log(False)
        return (2, None)
#     if temporary:
    if prior_content == temporary and not same_is_okay:
        return (1, None)
    return (0, temporary)

    
def fill_blanks(target):
    sequence = ["gopher", "previous", str(target).lower()]
    Playback([(sequence, 0.0)])._execute()


        
