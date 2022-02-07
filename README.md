# Random code for random fun

## nerdle

[nerdle.py](./nerdle/nerdle.py) is a python script that will list out two column tables providing equations that cover all digits and operations in nerdle. For each table, the columns contain the same digits but may differ in operations (digits listed in column header). There may be more or fewer equations in one column versus the other. Example:

```
-------------------------------
|  0 1 2 3 4   |   5 6 7 8 9  |
---------------+---------------
4 - 12 / 3 = 0 | 5 + 7 * 9 = 68
12 / 4 - 0 = 3 | 9 + 8 * 6 = 57
 3 - 4 / 2 = 1 | 9 + 7 * 8 = 65
12 / 3 - 4 = 0 | 7 * 8 + 9 = 65
12 / 4 - 3 = 0 | 7 * 9 + 5 = 68
12 / 3 - 0 = 4 | 9 + 6 * 8 = 57
3 - 12 / 4 = 0 | 5 + 9 * 7 = 68
0 + 12 / 4 = 3 | 8 * 6 + 9 = 57
 4 / 2 + 1 = 3 | 6 * 8 + 9 = 57
12 / 4 + 0 = 3 | 9 + 8 * 7 = 65
 1 + 4 / 2 = 3 | 8 * 7 + 9 = 65
0 + 12 / 3 = 4 | 9 * 7 + 5 = 68
12 / 3 + 0 = 4 | 9 * 8 - 67 = 5
3 * 2 + 4 = 10 | 57 - 6 * 8 = 9
0 + 4 * 3 = 12 | 8 * 9 - 65 = 7
3 * 4 + 0 = 12 | 65 - 7 * 8 = 9
4 * 3 + 0 = 12 | 9 * 8 - 7 = 65
4 + 3 * 2 = 10 | 68 - 7 * 9 = 5
2 * 3 + 4 = 10 | 57 - 8 * 6 = 9
4 + 2 * 3 = 10 | 68 - 9 * 7 = 5
0 + 3 * 4 = 12 | 8 * 9 - 67 = 5
               | 8 * 9 - 5 = 67
               | 9 * 8 - 5 = 67
               | 65 - 8 * 7 = 9
               | 8 * 9 - 7 = 65
               | 9 * 8 - 65 = 7
               | 96 / 8 - 5 = 7
               | 96 / 8 - 7 = 5
-------------------------------
```

Here we are considering the partition of digits where one set of equations use the first five digits and the second uses the last five digits. Pick one equation from the left and one equation from the right and you will get as much information as possible. I try to choose a pair where the two digit numbers are on different sides of the equations.

The script can be run with `python nerdle.py` or `./nerdly.py`. The output can be seen [here](./nerdle/output.txt).
