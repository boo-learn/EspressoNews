def find_button_index(button_text, button_object):
    for i, row in enumerate(button_object.inline_keyboard):
        for j, button in enumerate(row):
            if button.text == button_text:
                return i, j
    return None