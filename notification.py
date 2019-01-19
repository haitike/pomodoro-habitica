from importlib import util
import contextlib
import os

notify2_spec = util.find_spec("notify2")
if notify2_spec:
    import notify2
    notify2.init("Test")

pygame_spec = util.find_spec("pygame")
if pygame_spec:
    with contextlib.redirect_stdout(None):
        from pygame import mixer
        mixer.init()

script_dir = os.path.dirname(__file__)
pomodoro_audio = os.path.join(script_dir, "pomodoro.wav")
break_audio = os.path.join(script_dir, "break.wav")


def notification(type, task="Task"):
    if notify2_spec:
        if type == 0:
            notify2.Notification("Task completed", "{} was completed!".format(task)).show()
        elif type == 1:
            notify2.Notification("Break completed", "Break finished!").show()
    else:
        print("You don't have Notify2 module installed")

    if pygame_spec:
        if type == 0:
            song = mixer.Sound(pomodoro_audio)
            mixer.Sound.play(song)
        elif type == 1:
            song = mixer.Sound(break_audio)
            mixer.Sound.play(song)
    else:
        print("Install Pygame module for audio notification")
