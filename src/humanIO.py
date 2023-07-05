import datetime

TOGGLE_ON = True


def printh(message, recipient='Game', addSpacing=False, end='\n') -> None:
    # Check if print is enabled
    if not TOGGLE_ON:
        return

    # Get current time
    now = datetime.datetime.now().strftime("%H:%M:%S")

    # print message
    print(f"[{now}] - {recipient:<{13}} - {message}", end=end)
    # Add empty line if specified
    if addSpacing:
        print()


def inputh():
    printh('', recipient='Input', end='')
    return input()

