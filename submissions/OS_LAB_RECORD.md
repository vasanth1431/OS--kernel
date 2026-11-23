# Operating Systems Lab Record
**Student Name**: vasanth (Tadigotla Vasanth Diwakar)  
**Hostname**: VASANTH  
**USN**: `25BTRCL270` | **Course**: 25PCCS201 – Operating Systems Laboratory  
**Institution**: Faculty of Engineering & Technology (FET), Jain (Deemed-to-be University)  

---

## Experiment 1 – Basics of UNIX Commands

### 1.1 Aim
To study and execute basic UNIX commands for directory listing, system information, file operations, and permissions.

```bash
vasanth@VASANTH:~$ date
Tue Oct 13 05:52:19 UTC 2026
vasanth@VASANTH:~$ date +%m
10
vasanth@VASANTH:~$ date +%h
Oct
vasanth@VASANTH:~$ date +%d
13
vasanth@VASANTH:~$ date +%y
26
vasanth@VASANTH:~$ cal
    October 2026      
Su Mo Tu We Th Fr Sa  
             1  2  3  
 4  5  6  7  8  9 10  
11 12 13 14 15 16 17  
18 19 20 21 22 23 24  
25 26 27 28 29 30 31  

vasanth@VASANTH:~$ echo "text"
text
vasanth@VASANTH:~$ ls
vasanth hi irwed jain jain1 lab2 lab2.c lab2th lab2th.c sample.txt smallest-digit stud
vasanth@VASANTH:~$ cd ~/os_lab1
vasanth@VASANTH:~/os_lab1$ echo "Operating Systems Lab" > file1.txt
vasanth@VASANTH:~/os_lab1$ cat file1.txt
Operating Systems Lab
vasanth@VASANTH:~/os_lab1$ cp file1.txt file2.txt
vasanth@VASANTH:~/os_lab1$ mv file2.txt renamed.txt
vasanth@VASANTH:~/os_lab1$ wc -l file1.txt
1 file1.txt
vasanth@VASANTH:~/os_lab1$ head -n 1 file1.txt
Operating Systems Lab
vasanth@VASANTH:~/os_lab1$ tail -n 1 file1.txt
Operating Systems Lab
```

---

### 1.2 Aim
To write and execute a C program using the UNIX directory operations `opendir()`, `readdir()`, and `closedir()` to display the contents of a specified directory.

---

### 1.3 Aim – Simulate `cp` Command in C
To write and execute a C program to simulate the UNIX `cp` command by copying the contents of one file into another file.

```c
#include <stdio.h>

int main(int argc, char *argv[]) {
    FILE *src, *dest;
    int ch;
    if (argc != 3) {
        printf("Usage: %s source destination\n", argv[0]);
        return 1;
    }
    src = fopen(argv[1], "r");
    if (src == NULL) { perror("Source file"); return 1; }
    dest = fopen(argv[2], "w");
    if (dest == NULL) { perror("Destination file"); fclose(src); return 1; }
    while ((ch = fgetc(src)) != EOF) fputc(ch, dest);
    fclose(src);
    fclose(dest);
    printf("File copied successfully.\n");
    return 0;
}
```

**Execution Output:**
```bash
vasanth@VASANTH:~/os_lab3$ gcc simulate_cp.c -o simulate_cp
vasanth@VASANTH:~/os_lab3$ echo "Operating Systems Lab 3" > source.txt
vasanth@VASANTH:~/os_lab3$ ./simulate_cp source.txt destination.txt
File copied successfully.
vasanth@VASANTH:~/os_lab3$ cat destination.txt
Operating Systems Lab 3
```

---

### 1.4 – Shell Programming Basics
**Aim**: To write and execute simple shell programs using conditional statements, branching, and looping statements.

#### Program 1: Even or Odd
```bash
#!/bin/bash
echo "Enter the Number"
read n
if [ $((n % 2)) -eq 0 ]
then
    echo "$n is Even number"
else
    echo "$n is Odd number"
fi
```
```bash
vasanth@VASANTH:~/os_lab3$ chmod +x even_odd.sh
vasanth@VASANTH:~/os_lab3$ ./even_odd.sh
Enter the Number
24
24 is Even number
```

#### Program 2: Leap Year
```bash
#!/bin/bash
echo "Enter the year"
read y
if (( y % 400 == 0 || ( y % 4 == 0 && y % 100 != 0 ) ))
then
    echo "$y is a leap year"
else
    echo "$y is not a leap year"
fi
```
```bash
vasanth@VASANTH:~/os_lab3$ ./leap_year.sh
Enter the year
2027
2027 is not a leap year
```

#### Program 4: Swap Two Integers
```bash
#!/bin/bash
echo "Enter Two Numbers"
read a b
temp=$a
a=$b
b=$temp
echo "After swapping:"
echo "$a $b"
```
```bash
vasanth@VASANTH:~/os_lab3$ ./swap.sh
Enter Two Numbers
1 3
After swapping:
3 1
```

---

## Chapter 3 – Processes

### Lab 3.20 – PID Management Using a Bitmap
**Aim**: Implement a Process ID (PID) manager using a bitmap in Python 3, supporting PID allocation, release, and management within the range of 300 to 5000.
```bash
vasanth@VASANTH:.../3.20$ python3 pid_manager.py
Allocated PIDs: [300, 301, 302, 303, 304]
After releasing one PID: 302
```

### Lab 3.21 & 3.22 – Collatz Sequence
**Aim**: Create a child process to generate and print the Collatz sequence (with and without shared memory).
```bash
vasanth@VASANTH:.../3.22$ python3 collatz.py 10
Child process terminated with status 0
10 5 16 8 4 2 1
vasanth@VASANTH:.../3.22$ python3 collatz.py 7
7 22 11 34 17 52 26 13 40 20 10 5 16 8 4 2 1
```

### Lab 3.26 – Bidirectional IPC Using Pipes
**Aim**: Parent sends a message to child; child reverses case and sends it back.
```bash
vasanth@VASANTH:.../3.26$ python3 reverse_case.py
Child terminated with status 0
altered message:
tHIS IS A MESSAGE
```

### Chapter 3.2 – UNIX Shell Project
**Aim**: Implement a simple UNIX shell supporting history (`!!`), one pipe, redirection, and background execution.
```bash
vasanth@VASANTH:...$ python3 shell.py
myshell>> pwd
/home/vasanth/Operating-System-Concepts/Chapter 3.2 - UNIX Shell project
myshell>> echo Hello World
Hello World
myshell>> !!
echo Hello World
Hello World
```

### Chapter 3.3 – Task Information from `/proc`
```bash
vasanth@VASANTH:...$ echo 260
549
vasanth@VASANTH:...$ python3 pid.py 549
command = [bash] -- pid = [549] -- state = [S]
```

---

## Chapter 4 – Threads & Concurrency

### Practical 4.22 – Multithreading and Shared Results
**Aim**: Use three separate threads to calculate average, minimum, and maximum concurrently.
```bash
vasanth@VASANTH:...$ python3 main.py 10 20 30 40 50
Average: 30.00
Minimum: 10
Maximum: 50
```

### Practical 4.2 – Sudoku Solution Validator
**Aim**: Multithreaded validator checking rows, columns, and 3×3 subgrids with 27 worker threads.
```bash
vasanth@VASANTH:...$ python3 main.py sudoku_solution.txt
Valid solution!
```

### Practical 4.3 – Multithreaded Sorting
```bash
vasanth@VASANTH:...$ python3 main.py 10
The sorted array is:
 4742 10773 18328 26526 29835 66217 73658 81088 96956 99638
```

---

## Chapter 6 & 7 – Synchronization Tools & Classical Problems
- **Chapter 6**: Thread-safe resource manager using a mutex to prevent race conditions.
- **7.01 Bounded Buffer (Producer-Consumer)**: Implemented using semaphores, mutexes, and shared circular buffer.
- **7.02 Readers-Writers Problem**: Implemented with reader count, write mutex, and starvation prevention.
- **7.03 Dining Philosophers Problem**: Implemented with threads, mutex locks, and condition variables.

---

## Chapter 8 – Deadlocks

### Practical 8.01 – Banker's Algorithm
**Aim**: Implement Banker's Algorithm for deadlock avoidance and determine if the system is in a safe state.

### Practical 8.02 – Deadlock Detection
```text
Deadlock Detection Simulation
--------------------------------
Available Resources: [0, 0, 0]
Deadlock detected!
Deadlocked Processes: P0 P1 P2
```

### Practical 8.03 – Deadlock Prevention
**Technique**: Always acquire resources in a strict global hierarchy (eliminating circular wait).
```text
Process 1 is waiting for resources
Process 1 acquired Resource 1
Process 2 is waiting for resources
Process 1 acquired Resource 2
Process 1 is using both resources
Process 1 released both resources
Process 2 acquired Resource 1
Process 2 acquired Resource 2
Process 2 is using both resources
Process 2 released both resources
Deadlock Prevention Demonstrated!
```

---

## Chapter 9 to 14 – Memory, Storage & File Systems
- **Chapter 9: Main Memory**:
  - `9.01` Fixed Partition Allocation (Best-Fit, First-Fit, Worst-Fit).
  - `9.02` Dynamic Partition Allocation.
  - `9.03` Page Table Address Translation.
- **Chapter 10: Virtual Memory**:
  - `10.01` FIFO Page Replacement.
  - `10.02` LRU Page Replacement.
  - `10.03` Optimal Page Replacement.
  - `10.04` Comparison & Thrashing Simulation.
- **Chapter 11: Mass Storage Structure**:
  - `11.01` Disk Scheduling (FCFS, SSTF, SCAN, C-SCAN).
  - `11.02` Disk Access Time & Seek Calculation.
- **Chapter 12: I/O Systems**: I/O Scheduling, Buffering, Caching, and Spooling.
- **Chapter 13: File-System Interface**: Directory Operations and Directory Tree Traversal.
- **Chapter 14: File-System Implementation**: Contiguous, Linked, and Indexed File Allocation.
