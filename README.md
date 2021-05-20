# Sliding Windows Mapper
Many-core mapping heuristic based on sliding windows

## Pre-requisites

* Python3;
* Numpy;
* [Memphis Debugger](https://github.com/gaph-pucrs/MA-Memphis/blob/master/docs/Debugger.md)

## Running

Run:
```
python3 swm.py N P --w 3 --stride 2
```

Parameters:
* **N:** Many-core size (in X and Y);
* **P:** Number of pages per many-core PE;
* **w:** Optional: minimum sliding window size. Default: 3;
* **stride:** Optional: sliding window stride. Default: 2.
