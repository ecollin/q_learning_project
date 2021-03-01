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

`action_num_to_obj` - Given the number of an action, this function finds the block number and dumbbell color involved in the action, and returns a `RobotMoveDBToBlock` object holding this encoding of the action. The block number is found by the result of `action % 3` and the color is found with the value of `(action - block_num) // 3`. This makes sense because the block numbers change from 1-3 by increasing by 1 and modding 3 as you go through the action numbers, and the DB color changes as action goes up by 3. 

`do_qlearn` - Every iteration until convergence, this function calls `get_rand_action` to get a random action to perform. Assuming there is one (ie the world does not need t oreset), this is converted to a `RobotMoveDBToBlock` with `action_num_to_obj`, and then the action is published. After a `rospy.sleep(1.0)`, the action should be performed.

### Updating the Q-matrix
### Determining when to stop iterating through the Q-learning algorithm
### Executing the path most likely to lead to receiving a reward after the Q-matrix has converged on the simulated Turtlebot3 robot
## Robot perception description: Describe how you accomplished each of the following components of the perception elements of this project in 1-3 sentences, any online sources of information/code that helped you to recognize the objects, and also describe what functions / sections of the code executed each of these components (1-3 sentences per function / portion of code):
### Identifying the locations and identities of each of the colored dumbbells
### Identifying the locations and identities of each of the numbered blocks
## Robot manipulation and movement: Describe how you accomplished each of the following components of the robot manipulation and movement elements of this project in 1-3 sentences, and also describe what functions / sections of the code executed each of these components (1-3 sentences per function / portion of code):
### Moving to the right spot in order to pick up a dumbbell
### Picking up the dumbbell
### Moving to the desired destination (numbered block) with the dumbbell
### Putting the dumbbell back down at the desired destination
## Challenges (1 paragraph): Describe the challenges you faced and how you overcame them.
## Future work (1 paragraph): If you had more time, how would you improve your implementation?
## Takeaways (at least 2 bullet points with 2-3 sentences per bullet point): What are your key takeaways from this project that would help you/others in future robot programming assignments working in pairs? For each takeaway, provide a few sentences of elaboration.
