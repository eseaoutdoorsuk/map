import time
import pyautogui
from utils import *

###
### Run with python whatsapp.py
### Close WhatsApp beforehand
### 

def update_whatsapp_numbers():
    spreadsheet = get_spreadsheet()
    records = read_spreadsheet(spreadsheet, sheet="Form responses 2")
    wa_sheet = read_spreadsheet(spreadsheet, sheet="whatsapp")

    checked_numbers = [str(row["number"]) for row in wa_sheet]
    
    user_numbers = [str(record["number_clean"]) for record in records]

    numbers_to_check = [x for x in user_numbers if x not in checked_numbers and x != ""]

    print(f"{len(numbers_to_check)} numbers to check")
    print("To check:", numbers_to_check)
    setup_wa()
    in_group = search_numbers(numbers_to_check)

    status = write_spreadsheet([
        [num, in_g] for num, in_g in zip(numbers_to_check, in_group)
    ], spreadsheet, "whatsapp")
    return status

def setup_wa():
    time.sleep(1)

    pyautogui.press('win')
    time.sleep(1)

    pyautogui.write('whatsapp', interval=0.01)
    time.sleep(1)

    pyautogui.press('enter')
    time.sleep(2)

    with pyautogui.hold('win'):
        pyautogui.press('up')

    pyautogui.click(487, 193, duration=1); time.sleep(0.1)

    pyautogui.write('ESEA Outdoors welcome group', interval=0.01)

    pyautogui.click(436, 293, duration=1); time.sleep(0.1)

    pyautogui.click(1284, 90, duration=1); time.sleep(0.1)

    pyautogui.click(763, 163, duration=1); time.sleep(0.1)

def search_numbers(numbers):
    pyautogui.click(978, 198, duration=1); time.sleep(0.1)
    in_group = []
    for number in numbers:
        pyautogui.write(number, interval=0.05)

        try:
            box = pyautogui.locateOnScreen('api/img.png')
            number_in_group = box.top > 500
        except:
            number_in_group = False
            print("Error")

        pyautogui.press('backspace', presses=20, interval=0.05)
        print(f"{number} {'not ' if not number_in_group else ''}in group")
        in_group += [number_in_group]
    return in_group
    
if __name__ == "__main__":
    update_whatsapp_numbers()