class StateItem:
    def __init__(self, key, text, func=None, exits=False):
        self.key = key
        self.text = text
        self.func = func
        self.exits = exits

    def get_line_text(self):
        return "{}\t {}\n".format(self.key, self.text)

    def run(self):
        if self.func:
            self.func()

    def is_exit_item(self):
        return self.exits

    def get_key(self):
        return self.key


class MenuState:
    def __init__(self, name, top_text="", input_text="Input a key"):
        self.name = name
        self.items = list()
        self.top_text = top_text
        self.input_text = input_text

    def append_item(self, item):
        self.items.append(item)

    def delete_item(self, item):
        for idx, _item in enumerate(self.items):
            if item == _item:
                del self.items[idx]
                return True
        return False

    def get_menu_text(self):
        text = ""
        if self.top_text:
            text += self.top_text
            text += "\n\n"
        for i in self.items:
            text += i.get_line_text()

        return text

    def get_input_text(self):
        return "{}: ".format(self.input_text)

    def get_key_list(self):
        key_list = list()
        for item in self.items:
            key_list.append(item.get_key())
        return key_list

    def run_item(self, key):
        for item in self.items:
            if item.get_key() == key:
                item.run()

    def check_exit(self, key):
        for item in self.items:
            if item.get_key() == key:
                if item.is_exit_item():
                    return True

class Menu:
    def __init__(self):
        self.states = list()
        self.current_state = 0
        self.running = False

    def append_state(self, state):
        self.states.append(state)

    def delete_state(self, state):
        for idx, _state in enumerate(self.states):
            if state == _state:
                del self.states[idx]
                return True
        return False

    def start_main_loop(self):
        self.running = True
        while self.running:
            self.print_menu()
            self.input_key()

    def stop(self):
        self.running = False

    def print_menu(self):
        state = self.states[self.current_state]
        menu_text = state.get_menu_text()
        print(menu_text)

    def input_key(self):
        state = self.states[self.current_state]
        code_input = input(state.get_input_text())
        if self.check_input_key(code_input):
            state.run_item(code_input)
            if state.check_exit(code_input):
                self.stop()
        else:
            return False

    def check_input_key(self, input_key):
        key_list = self.states[self.current_state].get_key_list()
        if input_key not in key_list:
            return False
        else:
            return True

    def next_state(self):
        self.current_state += 1

    def previous_state(self):
        self.current_state -= 1

