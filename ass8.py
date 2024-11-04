# Packages: z3-solver, pandas
from z3 import *
import pandas as pd
import matplotlib.pyplot as plt

amount_of_people = 7
amount_of_monthly_tasks = 7
amount_of_weekly_tasks = 5

# T % 4 == 0 is monthly task week
T = 12

task_assignment = [[Int(f'task_{week}_{person}') for person in range(amount_of_people)] for week in range(T)]

rests = [Int(f'rests_{person}') for person in range(amount_of_people)]

solver = Optimize()

# Tasks can only range from task 1 to task weekly/monthly task (and 0 which means rest)
for week in range(T):
    if week % 4 == 0:
        for person in range(amount_of_people):
            solver.add(task_assignment[week][person] >= 0, task_assignment[week][person] <= amount_of_monthly_tasks)
    else:
        for person in range(amount_of_people):
            solver.add(task_assignment[week][person] >= 0, task_assignment[week][person] <= amount_of_weekly_tasks)

# Every task needs to be assigned exactly once
for week in range(T):
    tasks_per_week = amount_of_monthly_tasks if week % 4 == 0 else amount_of_weekly_tasks
    solver.add(
        Sum([If(task_assignment[week][person] >= 1, 1, 0) for person in range(amount_of_people)]) == tasks_per_week)

    for person1 in range(amount_of_people):
        for person2 in range(person1 + 1, amount_of_people):
            solver.add(Or(task_assignment[week][person1] == 0,
                          task_assignment[week][person2] == 0,
                          task_assignment[week][person1] != task_assignment[week][person2]))

# Make sure that people don't do the same task 2 weeks after each other or the same tasks 2 months after each other
for person in range(amount_of_people):
    for week in range(T - 1):
        solver.add(task_assignment[week][person] != task_assignment[week + 1][person])
    for week in range(T - 4):
        if week % 4 == 0:
            solver.add(task_assignment[week][person] != task_assignment[week + 4][person])


# Person specific task restrictions
# Common tasks: 0, 1, 2
# Monthly common tasks: 6, 7
# Downstairs: 3
# Upstairs: 4, 5
for week in range(T):
    for person in range(amount_of_people):
        if person in [0, 1, 2]:
            solver.add(Or(task_assignment[week][person] == 0, task_assignment[week][person] == 1,
                          task_assignment[week][person] == 2, task_assignment[week][person] == 3,
                          task_assignment[week][person] == 6, task_assignment[week][person] == 7))
        elif person in [3, 4, 5, 6]:
            solver.add(Or(task_assignment[week][person] == 0, task_assignment[week][person] == 1,
                          task_assignment[week][person] == 2, task_assignment[week][person] == 4,
                          task_assignment[week][person] == 5, task_assignment[week][person] == 6,
                          task_assignment[week][person] == 7))

# region rests

# Calculate rest counts
for person in range(amount_of_people):
    solver.add(rests[person] == Sum([If(task_assignment[week][person] == 0, 1, 0) for week in range(T)]))

# Define max_rests and min_rests manually
max_rests = Int('max_rests')
min_rests = Int('min_rests')

# Bounds for rests
solver.add(max_rests <= T)
solver.add(min_rests >= 0)

# Max of rests: max_rests >= rests[person] for all people
for person in range(amount_of_people):
    solver.add(max_rests >= rests[person])

# Min of rests: min_rests <= rests[person] for all people
for person in range(amount_of_people):
    solver.add(min_rests <= rests[person])

# endregion


# Small optimizations for the solver
# solver.set("timeout", 100000)

# Minimize the difference between max_rests and min_rests
solver.minimize(max_rests - min_rests)

if solver.check() == sat:
    model = solver.model()

    columns = [f"Week {week}" for week in range(T)]
    row_names = ['Downstairs bathroom', 'Shower', 'Downstairs kitchen', 'Upstairs bathroom', 'Upstairs kitchen',
                 'Vacuum', 'Outside']
    rows = [[] for _ in range(len(row_names))]

    for week in range(T):
        print(f"week {week}")
        for person in range(amount_of_people):
            task = model[task_assignment[week][person]].as_long()
            if task > 0:
                print(f"  Task {row_names[task - 1]} is done by room {person + 1}")
                rows[task - 1].append(person + 1)
        if week % 4 != 0:
            rows[amount_of_monthly_tasks - 2].append('')
            rows[amount_of_monthly_tasks - 1].append('')

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    df = pd.DataFrame(rows, columns=columns, index=row_names)
    print(df)
else:
    print("No solution found")
