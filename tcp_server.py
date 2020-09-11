"""
TCP server that has to find firstly the position of the
robot by moving him hither and thither then
the robot sends his position and then firstly
the robot is instructed by commands to go to the top left corner
of the box then that robot is instructed to go in
an inner circle in the box and after every move in the box it has to
try lift up the treasure if there is otherwise it
has to go further during the processing the server must be able to
cope with different problems via the Internet like delay,
segmentation or aggregated packet comes and also there are
conditions that those  packets incoming from the Robot
must comply for instance length, type of answers and so on.
"""
import socket
import threading

# SERVER and CLIENT PARAMETERS
##################################################################################

SERVER_KEY = 54621
CLIENT_KEY = 45328
TIMEOUT = 1
TIMEOUT_RECHARGING = 5
POSTFIX = "\\x07\\x08"
SERVER_MOVE = "102 MOVE\a\b".encode(encoding="UTF-8", errors="strict")
SERVER_TURN_LEFT = "103 TURN LEFT\a\b".encode(encoding="UTF-8", errors="strict")
SERVER_TURN_RIGHT = "104 TURN RIGHT\a\b".encode(encoding="UTF-8", errors="strict")
SERVER_PICK_UP = "105 GET MESSAGE\a\b".encode(encoding="UTF-8", errors="strict")
SERVER_LOGOUT = "106 LOGOUT\a\b".encode(encoding="UTF-8", errors="strict")
SERVER_OK = "200 OK\a\b".encode(encoding="UTF-8", errors="strict")
SERVER_LOGIN_FAILED = "300 LOGIN FAILED\a\b".encode(encoding="UTF-8", errors="strict")
SERVER_SYNTAX_ERROR = "301 SYNTAX ERROR\a\b".encode(encoding="UTF-8", errors="strict")
SERVER_LOGIC_ERROR = "302 LOGIC ERROR\a\b".encode(encoding="UTF-8", errors="strict")
CLIENT_RECHARGING = "RECHARGING\a\b".encode(encoding="UTF-8", errors="strict")
CLIENT_FULL_POWER = "FULL POWER\a\b".encode(encoding="UTF-8", errors="strict")

CLIENT_USER_NAME = 12
CLIENT_CONFIRMATION = 7
CLIENT_OK = 12
CLIENT_MESSAGE = 100
CLIENT_FULL_POWER_LEN = 12
CLIENT_RECHARGING_LEN = 12
####################################################################################

UP = 1
DOWN = 0
LEFT = -1
RIGHT = -2

####################################################################################

## SERVING FUNCTIONS


def is_correct_digit(num):
    for i in num:
        if i == " ":
            return False
        if not i.isdigit() and i != "-":
            return False
    return True


def check16_bit_num(num):
    try:
        int(num)
        if int(num) <= 65536 and is_correct_digit(num):
            return True
        else:
            return False
    except ValueError:
        return False


def check_lengths_strings(data, phase):
    if "\a" in data:
        length = len(data) + 1
    elif "\a\b" in data:
        length = len(data) + 2
    else:
        length = len(data)
    if "FULL POWER" in data:
        return length <= CLIENT_FULL_POWER_LEN
    if "RECHARGING" in data:
        return length <= CLIENT_RECHARGING_LEN
    if phase == 0:
        return length <= CLIENT_USER_NAME
    if phase == 1:
        return length <= CLIENT_CONFIRMATION
    if phase == 2:
        return length <= CLIENT_OK
    if "OK" in data and phase == 3:
        return length <= CLIENT_OK
    elif phase == 3 and "OK" not in data:
        return length <= CLIENT_MESSAGE
    elif phase == 4 and "OK" in data:
        return length <= CLIENT_OK
    elif phase == 4:
        return length <= CLIENT_MESSAGE


def check_lengths(data, phase):
    tmp = data.decode("utf-8")
    length = len(str(tmp)) + 2
    if "FULL POWER" in tmp:
        return length <= CLIENT_FULL_POWER_LEN
    if "RECHARGING" in tmp:
        return length <= CLIENT_RECHARGING_LEN
    if phase == 0:
        return length <= CLIENT_USER_NAME
    if phase == 1:
        return length <= CLIENT_CONFIRMATION
    if phase == 2:
        return length <= CLIENT_OK
    if "OK" in tmp and phase == 3:
        return length <= CLIENT_OK
    elif phase == 3 and "OK" not in tmp:
        return length <= CLIENT_MESSAGE
    elif phase == 4 and "OK" in tmp:
        return length <= CLIENT_OK
    elif phase == 4:
        return length <= CLIENT_MESSAGE


def set_initial_state_inside_box(current_direction):
    if current_direction == LEFT:
        return DOWN, SERVER_TURN_LEFT, 0
    elif current_direction == RIGHT:
        return DOWN, SERVER_TURN_RIGHT, 0
    elif current_direction == UP:
        return RIGHT, SERVER_TURN_RIGHT, 88888888888
    elif current_direction == DOWN:
        return DOWN, SERVER_MOVE, 0


def leave_only_coordinates(data):
    if not check16_bit_num(data.split(" ")[1]) or not check16_bit_num(data.split(" ")[2]):
        return 1, "", ""
    splitted = data.split(" ")
    x = int(splitted[1])
    y = int(splitted[2])
    if not (data[0] == "O" and data[1] == "K" and data[2] == " "):
        return 1, "", ""
    res = splitted[0] + " " + splitted[1] + " " + splitted[2]
    if res != data:
        return 1, "", ""
    return 0, x, y


def extract_messages_from_packets(src, phase, conn, MoreMsgInOne, current, total_messages):
    one_of_more = ""
    temporary = []
    if not MoreMsgInOne:
        while b"\a\b" not in src:
            if not check_lengths(src, phase):
                return 1, "", False, 0, 0
            conn.settimeout(1)
            nextdata = conn.recv(1024)
            src = src + nextdata
        if src.count(b"\a\b") == 0 or b"\a\b\a\b" in src:
            return 1, "error4", False, 0, 0
        ext = []
        tmp = src.decode("utf-8")
        for i in range(len(tmp)):
            if tmp[i] == "\x07" and tmp[i + 1] == "\x08":
                input = str("".join(ext))
                if not check_lengths_strings(input, phase):
                    return 1, "error1", False, 0, 0
                if (
                    not check16_bit_num(input)
                    and phase == 1
                    and "FULL POWER" not in tmp
                    and "RECHARGING" not in tmp
                ):
                    return 1, "error2", False, 0, 0
                if phase == 2 and "OK" in input:
                    ret_val, x, y = leave_only_coordinates(input)
                    if ret_val == 1:
                        return 1, "error3", False, 0, 0
                valid_input = 0
                return valid_input, str("".join(ext)), False, 0, 0
            else:
                ext.append(tmp[i])
    else:
        if total_messages + 1 != current:
            temporary = str(src)[2:-1].split("\\x07\\x08")
            temporary = list(filter(lambda g: (len(g) > 0), temporary))
            total_messages = len(list(temporary))
            one_of_more = temporary[current]
        if check_lengths_strings(one_of_more, phase):
            temp = temporary[current]
            current = current + 1
            if current == total_messages:
                MoreMsgInOne = False
            valid_input = 0
            return valid_input, temp, MoreMsgInOne, current, total_messages
        else:
            valid_input = 1
            return valid_input, "", False, 0, 0


def authentication_from_server(data):
    hash_sum = 0
    for i in range(len(data)):
        hash_sum += ord(data[i])
    hash_sum = hash_sum * 1000
    hash_conn = hash_sum % 65536
    hash_sum += SERVER_KEY
    mySum = hash_sum % 65536
    hash_sum = (str(mySum) + "\a\b").encode("utf-8")
    return hash_conn, hash_sum


def authentication_from_client(data, hash_conn):
    number = int(data)
    number += 65536 - CLIENT_KEY
    number %= 65536
    ret_code = 0
    if number == hash_conn:
        return ret_code
    else:
        ret_code = 1
        return ret_code


def pick_out_coordinates(data):
    coordinates_out = []
    retval = 0
    for i_tp in data:
        if not check16_bit_num(i_tp.split(" ")[1]) or not check16_bit_num(
            i_tp.split(" ")[2]
        ):
            retval = 1
            return retval, ""
        k = int(i_tp.split(" ")[1])
        j = int(i_tp.split(" ")[2])
        coordinates_out.append((k, j))
    return retval, coordinates_out


def get_robot_direction(curr_dir):
    x1 = curr_dir[0][0]
    y1 = curr_dir[0][1]
    x2 = curr_dir[1][0]
    y2 = curr_dir[1][1]
    if x1 == x2:
        if y2 > y1:
            return UP
        else:
            return DOWN
    else:
        if x2 > x1:
            return RIGHT
        else:
            return LEFT


def robot_move(last_x, last_y, direction):
    stage_completed = 0
    if last_y == 2 and last_x == -2:
        stage_completed = 1
        return direction, SERVER_PICK_UP, stage_completed
    if last_x < -2 and direction == UP and last_x != -2:
        return RIGHT, SERVER_TURN_RIGHT, stage_completed

    elif last_x > -2 and direction == UP and last_x != -2:
        return LEFT, SERVER_TURN_LEFT, stage_completed

    elif last_x < -2 and direction == DOWN and last_x != -2:
        return RIGHT, SERVER_TURN_LEFT, stage_completed

    elif last_x > -2 and direction == DOWN and last_x != -2:
        return LEFT, SERVER_TURN_RIGHT, stage_completed

    elif last_x < -2 and direction == LEFT and last_x != -2:
        return UP, SERVER_TURN_RIGHT, stage_completed

    elif last_x > -2 and direction == LEFT and last_x != -2:
        return LEFT, SERVER_MOVE, stage_completed

    elif last_x < -2 and direction == RIGHT and last_x != -2:
        return RIGHT, SERVER_MOVE, stage_completed

    elif last_x > -2 and direction == RIGHT and last_x != -2:
        return DOWN, SERVER_TURN_RIGHT, stage_completed

    elif last_y > 2 and direction == RIGHT and last_y != 2:
        return DOWN, SERVER_TURN_RIGHT, stage_completed

    elif last_y < 2 and direction == RIGHT and last_y != 2:
        return UP, SERVER_TURN_LEFT, stage_completed

    elif last_y > 2 and direction == LEFT and last_y != 2:
        return DOWN, SERVER_TURN_LEFT, stage_completed

    elif last_y < 2 and direction == LEFT and last_y != 2:
        return UP, SERVER_TURN_RIGHT, stage_completed

    elif last_y > 2 and direction == UP and last_y != 2:
        return DOWN, SERVER_TURN_RIGHT, stage_completed

    elif last_y < 2 and direction == UP and last_y != 2:
        return UP, SERVER_MOVE, stage_completed

    elif last_y > 2 and direction == DOWN and last_y != 2:
        return DOWN, SERVER_MOVE, stage_completed
    
    elif last_y < 2 and direction == DOWN and last_y != 2:
        return LEFT, SERVER_TURN_RIGHT, stage_completed


def MovingInsideBox(direction, x, y, offset):  # inward spiral
    if direction == DOWN:
        if -2 + offset < y:
            return DOWN, SERVER_MOVE
        else:
            return RIGHT, SERVER_TURN_LEFT
    if direction == RIGHT:
        if 2 - offset > x:
            return RIGHT, SERVER_MOVE
        else:
            return UP, SERVER_TURN_LEFT
    if direction == LEFT:
        if -2 + offset < x:
            return LEFT, SERVER_MOVE
        else:
            return DOWN, SERVER_TURN_LEFT
    if direction == UP:
        if 2 - offset > y:
            return UP, SERVER_MOVE
        else:
            return LEFT, SERVER_TURN_LEFT


def initialize(coordinates):
    last_x = coordinates[1][0]
    last_y = coordinates[1][1]
    cur_dir = get_robot_direction(coordinates)
    return last_x, last_y, cur_dir


def communication(sck, conn):
    phase = 0
    data_in = b""
    current = 0
    total_msg = 0
    MoreMsgInOne = False
    last_x = 9999999999
    last_y = 9999999999
    initial_direction_coordinates = []
    initial_direction = 9999999999
    cur_dir = 9999999999
    hash_conn = 0
    recharging_in_process = False
    Insideboxinit = 88888888888
    TimeToPickUp = False
    offset = 0
    corners = 1
    try:
        while True:
            if not MoreMsgInOne:
                data_in = conn.recv(1024)
            if data_in.count(b"\x07\x08") > 1 and not b"\a\b\a\b" in data_in:
                MoreMsgInOne = True
            ret, data, MoreMsgInOne, current, total_msg = extract_messages_from_packets(
                data_in, phase, conn, MoreMsgInOne, current, total_msg
            )
            if ret == 1:
                conn.sendall(SERVER_SYNTAX_ERROR)
                break
            if "RECHARGING" == data:
                conn.settimeout(5)
                recharging_in_process = True
                continue
            if "FULL POWER" == data:
                recharging_in_process = False
                conn.settimeout(1)
                continue
            if recharging_in_process:
                conn.sendall(SERVER_LOGIC_ERROR)
                break
            if phase == 0:
                hash_conn, data_back = authentication_from_server(data)
                conn.sendall(data_back)
                phase += 1
                if data_in.count(b"\x07\x08") == 1 and phase == 1:
                    if b"\0" in data_in and b"\x08" != data_in[-1:]:
                        conn.sendall(SERVER_SYNTAX_ERROR)
                        break
            elif phase == 1:
                ret = authentication_from_client(data, hash_conn)
                if ret == 0:
                    phase += 1
                    conn.sendall(SERVER_OK)
                    conn.sendall(SERVER_MOVE)
                else:
                    conn.sendall(SERVER_LOGIN_FAILED)
                    break
            elif phase == 2:
                initial_direction_coordinates.append(data)
                conn.sendall(SERVER_MOVE)
                phase += 1
            elif phase == 3:
                if (
                    initial_direction == 9999999999
                    and last_x == 9999999999
                    and last_y == 9999999999
                ):
                    if initial_direction_coordinates[0] == data:
                        conn.sendall(SERVER_MOVE)
                        continue
                    initial_direction_coordinates.append(data)
                    ret, initial_direction = pick_out_coordinates(
                        initial_direction_coordinates
                    )
                    if ret == 1:
                        conn.sendall(SERVER_SYNTAX_ERROR)
                        break
                    last_x, last_y, cur_dir = initialize(initial_direction)
                    cur_dir, data_to_send, stage_complete = robot_move(
                        last_x, last_y, cur_dir
                    )
                    conn.sendall(data_to_send)
                else:
                    retval, last_x, last_y = leave_only_coordinates(data)
                    if retval == 1:
                        conn.sendall(SERVER_SYNTAX_ERROR)
                        break
                    cur_dir, data_to_send, stage_complete = robot_move(
                        last_x, last_y, cur_dir
                    )
                    conn.sendall(data_to_send)
                    phase += stage_complete
            elif phase == 4:
                if data != "" and "OK" not in data:
                    conn.sendall(SERVER_LOGOUT)
                    break
                elif Insideboxinit == 88888888888:
                    cur_dir, data_to_send, Insideboxinit = set_initial_state_inside_box(
                        cur_dir
                    )
                    conn.sendall(data_to_send)
                    continue
                if data != "" and "OK" in data:
                    TimeToPickUp = True
                    splitted = data.split(" ")
                    last_x = int(splitted[1])
                    last_y = int(splitted[2])
                    if corners == 4:
                        offset += 1
                        corners = 0
                    if TimeToPickUp:
                        conn.sendall(SERVER_PICK_UP)
                        TimeToPickUp = False
                        continue
                    cur_dir, data_to_send = MovingInsideBox(
                        cur_dir, last_x, last_y, offset
                    )

                    if data_to_send == SERVER_TURN_LEFT:
                        corners += 1
                    conn.sendall(data_to_send)
                elif data == "":
                    cur_dir, data_to_send = MovingInsideBox(
                        cur_dir, last_x, last_y, offset
                    )
                    if data_to_send == SERVER_TURN_LEFT:
                        corners += 1
                    conn.sendall(data_to_send)
    except socket.timeout:
        print("Timeout!!!")
    finally:
        conn.close()


if __name__ == "__main__":
    PORT = 7000  # default port value
    test_value = 1
    try:
        PORT = int(input("Enter the port number: "))
    except ValueError:
        print("Wrong number now launch it again...")

    try:
        Threads = []
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ("localhost", PORT)
        mySocket.bind(server_address)
        mySocket.listen(1)
        print("Listenning on the localhost port: " + str(PORT))
        while 1:
            # Wait for a connection
            print("Waiting for new commands")
            connection, client_address = mySocket.accept()
            connection.settimeout(1)
            t1 = threading.Thread(target=communication, args=(mySocket, connection))
            t1.start()
            Threads.append(t1)
    except KeyboardInterrupt:
        print("The program was correctly ended")
