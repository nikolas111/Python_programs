"""
Program gets an array of characters 'o' and '!' in stdin
and then it simulates spreading of infection until the whole array is
infected
"""

import sys


def bfs(office, infected_people, rows):
    """
    Until isn't the whole square infected the infection is going
    """
    iteration = 0
    previous_plague = len(infected_people)
    while 1:
        for i in range(len(infected_people)):
            infected_people.extend(adjacent_neigbours(
                office, infected_people[i], infected_people, rows))
        if previous_plague == len(infected_people):
            break
        else:
            previous_plague = len(infected_people)
        iteration = iteration + 1
    print(f'Number of days to infect all:${iteration}')


def find_infected(office):
    """
    Get all infected
    """

    infected = []
    for i in range(len(office)):
        for j in range(len(office[i])):
            if office[i][j] == '!':
                infected.append(tuple([i, j]))
    return infected


def adjacent_neigbours(office, place, visited, rows):
    """
    Find infected the other day
    """

    spaces = []
    if place[0] - 1 >= 0:
        spaces.append((place[0] - 1, place[1]))
    if place[0] + 1 < rows:
        spaces.append((place[0] + 1, place[1]))
    if place[1] - 1 >= 0:
        spaces.append((place[0], place[1] - 1))
    if place[1] + 1 <= len(office) - 1:
        spaces.append((place[0], place[1] + 1))
    final = []
    for i in spaces:
        if office[i[0]][i[1]] == 'o' and i not in visited:
            final.append(i)
            office[i[0]][i[1]] = '!'
    return final


if __name__ == "__main__":
    print("Infekce:")
    matrix = []
    ROWS = 0
    infected_people = []
    for line in sys.stdin:
        ROWS = ROWS + 1
        matrix.append(list(line[:-1]))
    infected_people = find_infected(matrix)
    bfs(matrix, infected_people, ROWS)
