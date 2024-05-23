import argparse
import random
from sortedcontainers import SortedList


def parse_cmd_line_arguments():
    parser = argparse.ArgumentParser(description='Disk Scheduling Simulator')
    parser.add_argument('initial_position',
                        type=int,
                        choices=range(-4999, 5000),
                        help='Initial position of the disk arm in the range of -4999 to 4999')
    parser.add_argument('-f',
                        '--file',
                        type=str,
                        help='(OPTIONAL) File with disk track requests')
    return parser.parse_args()


def generate_disk_requests(filename, num_requests=100, disk_size=5000):
    if filename:
        with open(filename, 'r') as file:
            requests = [int(line.strip()) for line in file.readlines()]
    else:
        requests = [random.randint(0, disk_size - 1) for _ in range(num_requests)]
    return requests


# Divide requests into two lists based on their relation to the current position
def process_requests(position, requests):
    less = []
    more = []
    for request in requests:
        if request <= position:
            less.append(request)
        elif request > position:
            more.append(request)
    return less, more


# FCFS: Processes requests in the order they arrive, calculating the total arm movement distance sequentially
def first_come_first_serve(initial_position, requests):
    total_distance = abs(initial_position - requests[0])  # Distance to the first request
    for i in range(1, len(requests)):
        distance = abs(requests[i] - requests[i - 1])
        total_distance += distance  # Sum up the distance between consecutive requests
    return total_distance


# SSTF: Chooses the nearest request to the current head position to minimize total seek time
def shortest_seek_time_first(initial_position, requests):
    position = initial_position
    total_distance = 0

    requests = SortedList(requests)

    while requests:
        i = requests.bisect_left(position)  # Find insertion point that would keep list sorted
        # Find closest request (index of) to minimize arm movement
        if i == 0:  # No elements to the left, take the first element
            closest_request = requests.pop(0)
        elif i == len(requests):  # No elements to the right, take the last element
            closest_request = requests.pop(-1)
        else:
            left = requests[i - 1]
            right = requests[i]
            # Choose the closer of two elements around the index
            if position - left <= right - position:
                closest_request = left
            else:
                closest_request = right
            requests.remove(closest_request)

        distance = abs(position - closest_request)
        total_distance += distance
        position = closest_request

    return total_distance


# SCAN: Moves the head from one end of the disk to the other servicing requests, similar to an elevator
def scan_algorithm(initial_position, requests, disk_size=5000):
    direction = "right"  # Initial movement direction
    total_distance = 0
    position = initial_position

    sorted_requests = sorted(requests + [0, disk_size - 1])  # Includes the disk's bounds in the requests
    less, more = process_requests(position, sorted_requests)

    # If direction is right, process the more/greater than list first, then reverse
    if direction == "right":
        for request in more:
            total_distance += abs(position - request)
            position = request

        # After reaching the end, reverse the direction and process the 'less' list
        if less:
            total_distance += abs(position - 0)  # Move to start of disk before reversing direction
            position = 0
        for request in reversed(less):
            total_distance += abs(position - request)
            position = request

    else:  # If initial direction is left, reverse the order of processing
        for request in reversed(less):
            total_distance += abs(position - request)
            position = request
        # Reverse direction at the start of the disk
        if more:
            total_distance += abs(position - (disk_size - 1))  # Move to end of the disk before reversing
            position = disk_size - 1
        for request in more:
            total_distance += abs(position - request)
            position = request

    return total_distance


# C-SCAN: Moves the head in one direction, jumps back to the beginning once the end is reached, and continues
def circular_scan(initial_position, requests, disk_size=5000):
    position = initial_position
    total_distance = 0

    requests.copy().sort()

    # Calculate total distance based on position relative to the farthest request
    if position > requests[-1]:  # If past last request, wrap around disk to the start and then to the last request
        total_distance += disk_size - position + disk_size + requests[-1]
    elif position < requests[0]:  # If before the first request, move directly to the first request
        total_distance += requests[-1] - position
    else:
        total_distance += disk_size - position + disk_size + requests[-1] - requests[0]

    return total_distance


# LOOK: Similar to SCAN but reverses direction without reaching the disk's end if no further requests exist
def look_algorithm(initial_position, requests, disk_size=5000):
    position = initial_position
    total_distance = 0

    requests.copy().sort()

    # Calculates travel distance by considering the furthest request in the current direction of travel
    if position < requests[0] or position > requests[-1]:
        total_distance += abs(position - requests[0]) + abs(requests[-1] - requests[0])
    else:
        less, more = process_requests(position, requests)
        total_distance += max(position - min(less, default=position), max(more, default=position) - position)

    return total_distance


# C-LOOK: Similar to C-SCAN but only travels as far as the farthest request in one direction before reversing
def circular_look(initial_position, requests):
    position = initial_position
    total_distance = 0

    requests.copy().sort()

    if position > requests[-1]:
        total_distance += position - requests[0]
    elif position < requests[0]:
        total_distance += requests[-1] - position
    else:
        less, more = process_requests(position, requests)
        total_distance += requests[-1] - min(less) + max(more) - requests[0]

    return total_distance


def main():
    args = parse_cmd_line_arguments()
    requests = generate_disk_requests(args.file)

    print(f"FCFS: {first_come_first_serve(args.initial_position, requests)}")
    print(f"SSTF: {shortest_seek_time_first(args.initial_position, requests)}")
    print(f"SCAN: {scan_algorithm(args.initial_position, requests)}")
    print(f"C-SCAN: {circular_scan(args.initial_position, requests)}")
    print(f"LOOK: {look_algorithm(args.initial_position, requests)}")
    print(f"C-LOOK: {circular_look(args.initial_position, requests)}")


if __name__ == '__main__':
    main()
