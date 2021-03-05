# q_learning_project 

Enrique Collin and Jason Lin
# Implementation Plan
## Q-learning algorithm
### Executing the Q-learning algorithm
- We will encode the set of possible actions and states listed on the website and then follow the algorithm using the phantom robot node: until the Q-matrix converges, we will randomly select and perform an action and then update the Q-matrix using the reward published. 
- We can test this by observing (1) how long it takes for the Q matrix to converge (2) whether the robot's behavior is as desired after the Q matrix converges (3) manually inspecting the Q matrix.
### Determining when the Q-matrix has converged
- We will determine that the Q-matrix has converged by keeping track of the iteration when it last updated. If it has not updated for some number of iterations, perhaps 50, we will decide that it has converged. 
- We will test whether we chose too high/low a number of iterations by testing out different numbers and seeing if we need fewer/more iterations for the robot to achieve its goal using the ending Q matrix.
### Once the Q-matrix has converged, how to determine which actions the robot should take to maximize expected reward
- We will continuously (1) determine the current state (2) determine the desired next state to maximize expected reward (3) use the action matrix entry to find the action that moves between these states. 
- We will test this largely by whether the robot is able to achieve the goal of putting each dumbbell at the desired square.
## Robot perception
### Determining the identities and locations of the three colored dumbbells
- To determine the identity we can use the `/scan` topic and `/camera/rgb/image_raw` to detect the direction of the dumbbells and the color of them. When the robot is initialized, we will record its odometry as the starting position. When the robot needs to search for a dumbbell, it will return to this starting position and rotate until it detects the desired color.
- We can test by observing the robot’s behavior in RViz and perhaps looking at the actual identities and positions of the dumbells sent by the `ModelStates` publisher. 
### Determining the identities and locations of the three numbered blocks
- We will procure a neural network designed to detect arabic numerals in images. When the robot is initialized, we will have it use the `/scan` topic to locate the positions of the three blocks and store them in memory. In front of each of the blocks, the robot will use the neural network to process the camera feed from `/camera/rgb/image_raw` and calculate the probability of that block being 1, 2, or 3.
- We can test by observing the robot’s behavior in RViz and perhaps looking at the actual identities and positions of the blocks sent by the `ModelStates` publisher. 
## Robot manipulation & movement
### Picking up and putting down the dumbbells with the OpenMANIPULATOR arm
- Once navigating to the location of the dumbbell, we will make sure we are directly facing it at a set distance (this standardizes the needed grab command). Then, we will use the MoveIt package (which can detect collisions) to grab the dumbbell using a pre-determined through trial/error grab setting. 
- We can test by observing the robot’s behavior in RViz and editing behavior based on whether it is grabbing successfully or not. 
### Navigating to the appropriate locations to pick up and put down the dumbbells
- We can navigate to the right location using the initial position of the robot and the `/scan` topic; we will use proportional control. If needed, we will use the fact that dumbbells have color to tell which direction has the dumbbells and which has the blocks.
- We can test by observing the robot’s behavior in RViz and perhaps looking at the actual identities and positions of the blocks sent by the `ModelStates` publisher. 
## Time
- Enrique: Qlearn 
- Jason: Robot perception, arm manipulation
- We will work independently at our own paces on the portions of the project mentioned above until next Wednesday’s in-class studio time. At that point we will ideally be nearly finished with our sections and will pair program/redistributed work on the remaining parts of the project. 

# Writeup
## Objectives description (2-3 sentences): Describe the goal of this project.
The goal of this project was to implement a Q-learning algorithm that could train our robot to move certain colored dumbells in front of certain colored blocks. Aside from the Q-learning algorithm, crucial components of this also included implementing robot perception such that our robot could identify which blocks/dumbbells were which, and (2) implementing robot manipulation and movement such that the robot could move to the blocks/dummbells and grab the latter.


## High-level description (1 paragraph): At a high-level, describe how you used reinforcement learning to solve the task of determining which dumbbells belong in front of each numbered block.
We began by initializing a Q matrix storing an entry for every state-action combination possible, entries initialized to 0. Until this matrix converged, we did the following. First, we selected a random action from among all the possible actions and had the robot perform that action. We then waited for the reward to come in, at which point we updated the Q matrix based on the reward for that action and the Q-value at any of the possible achievable states from the state the action put us into (looking ahead). Eventually, the Q-matrix hadn't changed for some determined number of iterations of these steps, which we deemed convergence. This left us with a Q-matrix storing the values represented by each action in each state. Once this was done, we could (1) find the current state of the robot (2) find the action in the current state with maximum q-value and (3) execute that action; assuming the above steps of setting the Q-matrix worked, this would lead to the dumbbeels being in front of each numbered block since that would maximize the q-value. 

## Q-learning algorithm description: Describe how you accomplished each of the following components of the Q-learning algorithm in 1-3 sentences, and also describe what functions / sections of the code executed each of these components(1-3 sentences per function / portion of code):
### Selecting and executing actions for the robot (or phantom robot) to take
`get_rand_action` - Given a start state, this function looks at that state's row entry in the action_matrix, which holds a list of actions indexed by the state the actions lead to if performed; some of these state indices hold the value -1 to indicate that that state cannot be reached. This function randomly selects one of these actions and returns both it and the state it leads to.

`action_to_desc` - Given the number of an action, this function finds the block number and dumbbell color involved in the action, and returns a tuple of the form (DB_color, block number) representing the action. The block number is found by the result of `action % 3` and the color is found with the value of `(action - block_num) // 3`. This makes sense because the block numbers change from 1-3 by increasing by 1 and modding 3 as you go through the action numbers, and the DB color changes as action goes up by 3. 

`do_qlearn` - Every iteration until convergence, this function calls `get_rand_action` to get a random action to perform. Assuming there is one (ie the world does not need t oreset), this is converted to a `RobotMoveDBToBlock` using`action_to_desc`, and then the action is published. After a `rospy.sleep(1.0)`, the action should be performed.

### Updating the Q-matrix
`update_q`-The core of the QLearning algorithm is a Bellman equation that can be seen on the project website, this function essentially just runs that equation and updates the Q-matrix with the result.  It returns True if the updated value is different from the old value, and False otherwise (used for tracking last update for convergence). 

`publish_qmat`- If update-q returns True and the Q-matrix was updated, this function just converts its form in the QLearn class, which is a numpy array, to the QMatrix() object type, and publishes it. 

`do_qlearn`-In each iteration, after performing an action as described above, this function calls `update_q` and then `publish_qmat` if the former returned True, which handles updating the Q-matrix.  

### Determining when to stop iterating through the Q-learning algorithm
`do_qlearn`- This function keeps track of the current "iteration", which in this context just means the number of actions that have been performed, and the last iteration at which the Q-matrix update described above resulted in the Q-matrix changing at all (ie the last iteration in which `update_q` returned True). The function keeps going only while the difference between the current iteration number and iteration of the last update is sufficiently small; it stops when it gets high enough (we ended up choosing 300 after a stray run ended before convergence with a value of 200). 

### Executing the path most likely to lead to receiving a reward after the Q-matrix has converged on the simulated Turtlebot3 robot
`manipulator_action_received`-Callback for "manipulator_action" event that checks if the event's field `is_confirmation` is set to True, and if so sets `self.action_confirmation_received` to True. Used to interact with the movement/perception code to know when the last sent action was executed.

`get_action_end_state`-Given a state and valid action, returns the state of the world after applying the action in the given state.

`is_valid_action`-Given a state and action, determines if the action is valid in that state (ie if it moves a DB that is at origin to a previously unoccupied block).

`in_final_state`- Given a state, returns True if all the DBs are located at a block.

`execute_path_for_reward`-After the QMatrix converges, the QLearn object calls this function to execute the path most likely to receive a reward by sending actions to the movement/perception code one at a time. It iterates starting with `current_state = 0` while the current state is not a final state (using `in_final_state`) and finds the valid action in the current state with highest Q-value from the converged Q-matrix. It then publishes this action to "manipulator_action" topic where the movement and perception code will receive it and execute it, and sleeps until a confirmation event comes in from that code (ie `manipulator_action_received` sets `self.action_confirmation_received` to True), at which point it changes to the state after the action using `get_action_end_state` and moves on to the next iteration.

## Robot perception description: Describe how you accomplished each of the following components of the perception elements of this project in 1-3 sentences, any online sources of information/code that helped you to recognize the objects, and also describe what functions / sections of the code executed each of these components (1-3 sentences per function / portion of code):
### Identifying the locations and identities of each of the colored dumbbells
`vision.py` - We used the code from class meeting 03 to detect the centroid of a colored portion of an image. Upon receiving an action command to move a certain dumbbell to a certain block, we would apply a mask to the robot's camera feed in order to find the color centroids. Our bot rotates until it's facing a potential target, then stops and checks the camera feed to see if the target dumbbell is in the center of the image.
### Identifying the locations and identities of each of the numbered blocks
`vision.py` - We used the keras-ocr neural network in order to identify digits on the side of blocks. Upon receiving an action command to move a certain dumbbell to a certain block, we would have the bot rotate until it sees something right in front of it via laser scan. We would then process a raw camera image by feeding it into the neural network, which will give us the locations of identified characters. If the identified characters match the number of the block in the action command, we've found the appropriate block.
## Robot manipulation and movement: Describe how you accomplished each of the following components of the robot manipulation and movement elements of this project in 1-3 sentences, and also describe what functions / sections of the code executed each of these components (1-3 sentences per function / portion of code):
### Moving to the right spot in order to pick up a dumbbell
`movement.py` - We used callback functions and a state system to identify when the robot is facing a dumbbell and is right in front of it. The `vision.py` module process the camera feed and identifies pixel positions of dumbbells/blocks relative to the center of the bot's field of view. When the robot sees a colored dumbbell in the center of its field of view, it uses proportional control to approach the dummbbell for both linear and angular velocity based on the laser scan values of the object. This means that the bot is slower and more accurate as it gets closer to the dumbbell, which allows for precise movements.
### Picking up the dumbbell
`arm_manipulation.py` - We used MoveItCommander to set the joints of the arm to preset positions for grabbing the dumbbells and lifting them. These preset positions were determined by trial and error.
### Moving to the desired destination (numbered block) with the dumbbell
`movement.py` - Our code for moving to the blocks is the same as for moving to the dumbbells, just with different image center targets. The bot moves back to the center of the map with the dumbbell and turns until it sees an object, which it then scans. Just like with the dumbbells, proportional control is employed for precise movement.
### Putting the dumbbell back down at the desired destination
`arm_manipulation.py` - We used MoveItCommander to drop the dumbbell by resetting the arm joints to the positions they were in when the dumbbell was picked up.
## Challenges (1 paragraph): Describe the challenges you faced and how you overcame them.
In the QLearning section, the first challenge faced was figuring out how to initialize the action matrix and more generally convert between state/action numbers and what they meant. Solving this problem just took a lot of thought and unit tests for the individual functions. With regards to the actual algorithm, getting the rewards to be applied to the proper action/working with the reward events was quite tricky. Our first edition of the algorithm did not work, and after adding a pltethora of print statements, we determined that it seemed sometimes multiple rewards were sent for just one action. Many attempts at restructing the code failed to fix this, so eventually we just had the code ignore the first in a sequence of rewards, which somehow fixed it. In the perception and movement section, we split the finding and picking up of DBs before finding and moving to blocks into many different states, and likewise ran into many problems transitioning between them. One such challenge was that running an image through the neural network to detect a block number took 30 seconds, whereas we had expected it to be almost instant. This meant the robot kept turning to look for other objects while processing instead of stopping quickly on the object as expected. We overcame this by restructuring to stop turning when facing an object in order to process. 

## Future work (1 paragraph): If you had more time, how would you improve your implementation?
In the QLearning section, one thing we would look into more is the problem of multiple rewards being sent for one action described above. While we found a way to fix it by ignoring some of them, presumably there only should be one reward being sent per action, and perhaps we have some buggy code causing this. Another thing we might change is stop using a numpy matrix for the Q-matrix, because as is we do that and it requires converting to Python lists whenever we publish it, which is inefficent. In the perception and movement code, we have some more severe problems we would work on given more time. In particular, whenever the robot needs to go back to the center of the mapto spin and identify the next needed object, it mosey's around going in wrong directions for some time before eventually reaching the center. Given more time, we would fix this bug and make it go directly to the center. Another problem is that, though our robot moves the dumbbells to the blocks, it drops the dumbbells at the corners of the blocks on the sides of the map rather than in their middles. This means that reset world does not detect them and does not reset the world. Given more time, we would fix this. We might also consider restructuring our code so that instead of trying to identify objects by spinning around in the center of the map and stopping when passing over an object, we just used the fact that there are only 6 objects in the map to move over to each of them, identify them, and remember the locations to move back to using odometry. This structure may have been better, but we didn't have time to switch over to it. 

## Takeaways (at least 2 bullet points with 2-3 sentences per bullet point): What are your key takeaways from this project that would help you/others in future robot programming assignments working in pairs? For each takeaway, provide a few sentences of elaboration.
-Unit testing is crucial for something with so many moving parts. Writing a bunch of code and seeing at the end if it works or not, as I hoped might work out, leaves you clueless to what does work and what's broken if you make any mistakes. I ended up writing small te sts for different parts of the QMatrix code (ie, checking if I was sending actions right, converting actions and states to numbers properly, etc.) which was immensely helpful in pinpointing problems. 

-Planning ahead ahead is also crucial for such a large projet. While it is very tempting to just start programming and chipping away at the project, which I initially tried for the QMatrix code initializing the action matrix and converting between numbers and descriptions, my code quickly became unmanageable and unclear. Things went much more smoothly after I planned out how I wanted to map between the two. 

-Communicate more. We didn't communicate on progress much until the assignment neared the deadline, and so I (Enrique) didn't realize how difficult the perception and movement sectiosn were turning out to be. If we had talked more I would have realized there was much more work left to do. We would have collaborated on them sooner, doubling our productivity on them and perhaps letting us finish. 
