#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* concat(const char *s1, const char *s2)
{
    char *result = malloc(strlen(s1) + strlen(s2) + 1); // +1 for the null-terminator
    // in real code you would check for errors in malloc here
    strcpy(result, s1);
    strcat(result, s2);
    return result;
}

int which = 0;
int allocation = 0;
int maxAllocation = 10000;
char string[2] = "A";
char* current = string;
char* returnValue;

void findCombinationsUtil(int min, int size, int arr[], int index, int num, int reducedNum)
{
    if(allocation >= maxAllocation)
        return;
    if (index > size)
        return;
    // Base condition
    if (reducedNum < 0)
        return;

    // If combination is found, print it
    if (reducedNum == 0) {
        for (int i = 0; i < index; i++) {

            char indexString[arr[i]+1];
            itoa(arr[i], indexString, 10);

            if(which > 0) {
                returnValue = concat(current, indexString);
                free(current);
                current = returnValue;
            } else {
                returnValue = concat("", indexString);
                current = returnValue;
            }

            if (i < index - 1) {
                returnValue = concat(current, ",");
                free(current);
                current = returnValue;
            }

            which++;
        }
        allocation++;
        returnValue = concat(current, "\n");
        free(current);
        current = returnValue;
        return;
    }

    // Find the previous number stored in arr[]
    // It helps in maintaining increasing order
    int prev = (index == 0)? 3 : arr[index-1];

    // note loop starts from previous number
    // i.e. at array location index - 1
    for (int k = prev; k <= num ; k+=1)
    {
        // next element of array is k
        arr[index] = k;

        // call recursively with reduced number
        findCombinationsUtil(min, size, arr, index + 1, num, reducedNum - k);
    }
}




/**
 * Min, Max
 * @param argc
 * @param argv
 * @return
 */
int main(int argc, char* argv[])
{
    if(argc > 2) {
        int n = 25;
        int min = atoi(argv[1]);
        int max = atoi(argv[2]);
        int arr[n];

        findCombinationsUtil(min, max, arr, 0, 25, n);

        printf(current);
    }
    return 0;
}

