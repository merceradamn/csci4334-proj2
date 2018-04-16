# Adam Mercer
# CSCI4334 Oper Sys
# Project 2
"""
Times Format:
    Arrival Time    Service Time
    Integer         Float

Determine:
    Average wait time
    Average turnaround time

Graph 1:
    X-Axis: Context Switching Time
    Y-Axis: Average Wait Time

Graph 2:
    X-Axis: Context Switching Time
    Y-Axis: Average Turnaround Time
"""

from collections import deque

# Open the file and load them into a list for reading
def getList(fname):
    # Process List
    pl = []
    
    # Open given file
    with open(fname) as f:
        for line in f:
            #print(line, end="")
            line = line.strip('\n')
            items = line.split()
            
            pl.append([int(items[0]),float(items[1])])
            #print([int(items[0]),float(items[1])])
            
    # Return the list(queue)
    return pl

def getProcess(pl, pq, currTime, tq):
    # Check if next process in the list arrives before or during current time
    # Get an initial process from the list
    if len(pl) > 0:
        front = pl[0]
    else:
        return
    
    while(front[0] < currTime + tq):
        # Arrives within time quantum so queue it
        # [Arrival, Service, Remain, Time Finished, First Serviced, Wait Amount]
        process = [front[0], front[1], front[1], -1, -1, 0]
        pq.append(process) #Append to the queue
        pl.popleft() # Pop off the procList

        # Get the next process
        # Check the length of the procList
        if len(pl) > 0:
            front = pl[0]
        else:
            break

def printProcQueue(pq):
    print("Proc Queue: [Arriv, Serv, Rem, Fin'd, F. Serv ,T.Wait]")
    for p in pq:
        print('\t', p)

def handleProcess(procQueue, ct, tq, ft):
    # Get the first item from the queue
    frontOfQueue = procQueue.popleft()
    #print("Current Process: ", frontOfQueue)

    # Check if process arrives AFTER current time
    if(frontOfQueue[0] > ct):
        # Add to downtime
        ft += frontOfQueue[0] - ct
        #print("Free Time: ", ft)
        # Increase current time to match when this process arrives
        ct = frontOfQueue[0]
    
    # Check if this is the first time the process is being handled
    if(frontOfQueue[4] == -1):
        # Hasn't been serviced so record current time
        frontOfQueue[4] = ct
    
    # [Arrival, Service, Remain, Time Finished, First Serviced, Wait Amount]
    # Process service time shorter than quantum
    if frontOfQueue[2] <= tq:
        # Finish the process and return the current time
        frontOfQueue[3] = ct + frontOfQueue[2] # Set finish time
        frontOfQueue[2] = 0 # Set service time to zero

        timeElapsed = frontOfQueue[3] - ct
        ct += timeElapsed # Increase current time by amount process used
        
    elif frontOfQueue[2] > tq:
        # Process still has more time than quantum
        frontOfQueue[2] -= tq # Remove the quantum from the process
        ct += tq # Increase by quantum since we used it
        
    # Done processing the process
    procQueue.append(frontOfQueue) # Push process back into the queue
    return ct # Return the current time

################################################################################
# Variables

scale = 0 # Which scale are we using
fileToProcess = 0 # Which file are we processing

if(scale == 1):
    # Large Scale Values
    overhead = [0,5,10,15,20,25]
    timeQuant = [50,100,250,500]
else:
    # Actual Scale, milliseconds
    overhead = [0,0.005,0.010,0.015,0.020,0.025]
    timeQuant = [0.050,0.100,0.250,0.500]

fileTests = ["times.txt", "times_small.txt", "times_small2.txt"]
# Indexes to hold what quantum/dispatch
ohIndex = 0
tqIndex = 0

# Open a file to save the data to for later
results = open('results.txt', 'w')
results.write('[Arrival Time, Service Time, Time Remain, Time Finished, First Serviced, Wait Amount]\n')

for ohIndex in overhead:    
    for tqIndex in timeQuant:
        # Write what time quantum and dispatch this run is
        results.write('Quantum: %.4f \t Dispatch: %.4f\n' %(tqIndex, ohIndex))
        
        # Get the process list
        procList = deque(getList(fileTests[fileToProcess]))
        #print("Number of processes: ", len(procList))

        # Start scheduling
        currTime = 0
        timeElapsed = 0 # Added to each process when at front of queue
        procQueue = deque([])
        finishedProcesses = []
        freeTime = 0 # Total time processor isn't busy

        # Main loop that processes the processes
        while len(procQueue) > 0 or len(procList) > 0:
            #print("T= %4.6f Q:%5d L:%5d" %(currTime, len(procQueue), len(procList)))

            # Fetch processes that will arrive within the time quantum
            getProcess(procList, procQueue, currTime, tqIndex)

            # If the queue has items
            if procQueue:
                currTime = handleProcess(procQueue, currTime, tqIndex, freeTime)

                handledProc = procQueue.pop() # Get the most recent process
                if handledProc[2] == 0: # Check remain time
                    finishedProcesses.append(handledProc) # Add to finishedProcesses
                else:
                    procQueue.append(handledProc) # Put back in queue
                    # Add the context switching time to the processes in list

            else:
                #print("No items left in queue.")
                # Increment by time quantum since there's no process to queue
                currTime += tqIndex

            # Check the dispatch time and add it to the current time
            currTime += ohIndex
            

        # Loop that shows the results of the simulation
        #print("Finished with processes. Time to debrief...")
        #print("[Arr Time][Srv Time][Remain T][Time Fin][1st Serv][Wait Tme]")
        for fp in finishedProcesses:
            # Calculate wait time based on first service - arrival time
            fp[5] = fp[4] - fp[0]
            #print(fp)
            fpAsString = str(fp) # Cast list as a string to write to file
            results.write(fpAsString)
            results.write('\n')

        # Write an endline so we can start the next chunk
        #results.write('Free: %f\n\n' %freeTime)
        results.write('\n\n')
        
        #print("Done with a run.")

# Close the file now
results.close()
