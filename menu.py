class Item:
    autokey_index = 1

    def __init__(self, text, key=None, func=None):
        self.text = text
        self.func = func
        self.key = key
        if self.key:
            self.is_autokey = False
        else:
            self.is_autokey = True
            self.key = str(Item.autokey_index)
            Item.autokey_index += 1

    def get_line_text(self):
        if self.key:
            return "{:<5s}\t {}\n".format(self.key, self.text)
        else:
            return "{:<5s}\t {}\n".format("", self.text)

    def run(self):
        if self.func:
            self.func()
            return "func"
        else:
            return None


class ExitItem(Item):
    def __init__(self, text, key=None):
        Item.__init__(self, text, key)

    def run(self):
        return "exit"


class State:
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
        for item in sorted(self.items, key=lambda x: (x.is_autokey, x.key)):
            text += item.get_line_text()
        return text

    def get_key_list(self):
        key_list = list()
        for item in self.items:
            key_list.append(item.key)
        return key_list

    def run_item(self, key):
        for item in self.items:
            if item.key == key:
                return item.run()

    def get_input_text(self):
        return "{}: ".format(self.input_text)


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
            r = state.run_item(code_input)
            if r == "exit":
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
