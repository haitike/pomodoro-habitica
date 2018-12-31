class StateItem:
    def __init__(self, key, text, func):
        self.key = key
        self.text = text
        self.func = func

    def get_line_text(self):
        return "{}\t {}\n".format(self.key, self.text)


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

    def start(self):
        self.running = True
        while self.running:
            self.print_menu()

    def print_menu(self):
        state = self.states[self.current_state]
        menu_text = state.get_menu_text()
        print(menu_text)
        input(state.get_input_text())

    def stop(self):
        self.running = False

    def next_state(self):
        self.current_state += 1

    def previous_state(self):
        self.current_state -= 1

