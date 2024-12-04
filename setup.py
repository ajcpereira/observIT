import curses

def update_os():
    print("Updating OS...")

def change_network():
    print("Changing Network Settings...")

def change_keyboard():
    print("Changing Keyboard Layout...")

def change_timezone():
    print("Changing Timezone...")

def manage_containers():
    print("Managing Containers...")

def menu(stdscr):
    curses.start_color() 
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    menu_items = [
        "Update OS",
        "Change Network Settings",
        "Change Keyboard Layout",
        "Change Timezone",
        "Manage Containers",
        "Exit"
    ]

    current_row = 0

    while True:
        stdscr.clear()

        for idx, item in enumerate(menu_items):
            x = 1
            y = 1 + idx
            if idx == current_row:
                stdscr.addstr(y, x, item, curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == ord('\n'):
            match current_row:
                case 0:
                    update_os()
                case 1:
                    change_network()
                case 2:
                    change_keyboard()
                case 3:
                    change_timezone()
                case 4:
                    manage_containers()
                case 5:
                    break
            stdscr.clear()
            stdscr.refresh()
            stdscr.getch()

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(menu)
