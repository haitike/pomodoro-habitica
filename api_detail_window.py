import tkinter as tk
import configparser

class APIDetails(tk.Frame):
    def __init__(self, parent, user=None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.user = user
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.label = tk.Label(self, text="Introduce your API details from your Habitica profile")
        self.label.grid(row=0, column=0, columnspan=2)
        tk.Label(self, text="User ID").grid(row=1, column=0)
        tk.Label(self, text="API Key").grid(row=2, column=0)
        self.user_entry = tk.Entry(self)
        self.user_entry.grid(row=1, column=1)
        self.key_entry = tk.Entry(self)
        self.key_entry.grid(row=2, column=1)
        tk.Button(self, text="Save details", command=self.on_button).grid(row=3, column=0, columnspan=2)

    def on_button(self):
        self.user.set_headers(self.user_entry.get(), self.key_entry.get())
        success = self.user.update_profile()
        if success:
            config = configparser.ConfigParser()
            config.read("config.ini")
            if not config.has_section("HabiticaAPI"):
                config.add_section("HabiticaAPI")
            config.set("HabiticaAPI", "UserID", self.user_entry.get())
            config.set("HabiticaAPI", "APIKey", self.key_entry.get())
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            self.on_closing()
        else:
            self.label.config(text="Error: Your Habitica API details are incorrect", fg="red")

    def on_closing(self):
        self.parent.destroy()
