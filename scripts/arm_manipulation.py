#!/usr/bin/env python3

"""
Controller object handling all arm functions based on the robot state.
"""

import rospy
import moveit_commander
from sensor_msgs.msg import JointState
import constants as C
from q_learning_project.msg import ActionState, ArmRaised


def create_joint_state_msg(joint_names, joint_positions):
    """
    Create a JointState message from a list of names and joint positions.
    """
    joint_state = JointState()
    joint_state.name = joint_names
    joint_state.position = joint_positions
    return joint_state


class ArmController():
    """
    Tracks the robot's current state and moves the arm when necessary.
    """

    def __init__(self):
        rospy.init_node('q_arm')

        self.move_group_arm = moveit_commander.MoveGroupCommander("arm")
        self.move_group_gripper = moveit_commander.MoveGroupCommander(
            "gripper")
        self.current_state = C.ARM_STATE_IDLE

        self.publishers = self.initialize_publishers()
        self.initialize_subscribers()

    def initialize_publishers(self) -> dict:
        """
        Initialize all the publishers this node will use.
        """
        publishers = {}
        publishers[C.ARM_RAISED_TOPIC] = rospy.Publisher(
            C.ARM_RAISED_TOPIC, ArmRaised, queue_size=C.QUEUE_SIZE
        )
        return publishers

    def initialize_subscribers(self) -> None:
        """
        Initialize all the subscribers this node will use.
        """
        rospy.Subscriber(
            C.ACTION_STATE_TOPIC,
            ActionState,
            self.process_action_state)

    def set_state(self, state: str) -> None:
        """
        Move the arm when the controller changes to a new state.
        """
        if state == C.ARM_STATE_UP and self.current_state != C.ARM_STATE_UP:
            self.raise_arm()
            self.close_gripper()
        elif state == C.ARM_STATE_DOWN and self.current_state != C.ARM_STATE_DOWN:
            self.lower_arm()
            self.open_gripper()
        elif state == C.ARM_STATE_GRABBING and self.current_state != C.ARM_STATE_GRABBING:
            self.close_gripper()
            self.raise_arm()
        elif state == C.ARM_STATE_RELEASING and self.current_state != C.ARM_STATE_RELEASING:
            self.lower_arm()
            self.open_gripper()
        self.current_state = state

    def raise_arm(self) -> None:
        """
        Move the arm to a raised position and notify the action controller.
        """
        self.move_group_arm.go(
            joints=create_joint_state_msg(
                C.ARM_JOINT_NAMES,
                C.ARM_JOINT_GOAL_UP),
            wait=True)
        self.move_group_arm.stop()
        arm_raised_flag = ArmRaised()
        arm_raised_flag.arm_raised = True
        self.publishers[C.ARM_RAISED_TOPIC].publish(arm_raised_flag)

    def lower_arm(self) -> None:
        """
        Move the arm to a lowered position and notify the action controller.
        """
        self.move_group_arm.go(
            joints=create_joint_state_msg(
                C.ARM_JOINT_NAMES,
                C.ARM_JOINT_GOAL_DOWN),
            wait=True)
        self.move_group_arm.stop()
        arm_raised_flag = ArmRaised()
        arm_raised_flag.arm_raised = False
        self.publishers[C.ARM_RAISED_TOPIC].publish(arm_raised_flag)

    def close_gripper(self) -> None:
        """
        Close the gripper.
        """
        self.move_group_gripper.go(
            joints=create_joint_state_msg(
                C.GRIPPER_JOINT_NAMES,
                C.GRIPPER_JOINT_GOAL_CLOSED),
            wait=True)
        self.move_group_gripper.stop()

    def open_gripper(self) -> None:
        """
        Open the gripper.
        """
        self.move_group_gripper.go(
            joints=create_joint_state_msg(
                C.GRIPPER_JOINT_NAMES,
                C.GRIPPER_JOINT_GOAL_OPEN),
            wait=True)
        self.move_group_gripper.stop()

    def process_action_state(self, action_state):
        """
        Receive an action state and update the arm state accordingly.
        """
        new_state = action_state.action_state

        if new_state == C.ACTION_STATE_IDLE:
            self.set_state(C.ARM_STATE_IDLE)

        elif new_state == C.ACTION_STATE_MOVE_CENTER:
            self.set_state(C.ARM_STATE_UP)

        elif new_state == C.ACTION_STATE_LOCATE_DUMBBELL:
            self.set_state(C.ARM_STATE_DOWN)

        elif new_state == C.ACTION_STATE_CENTER_DUMBBELL:
            self.set_state(C.ARM_STATE_DOWN)

        elif new_state == C.ACTION_STATE_WAIT_FOR_COLOR_IMG:
            self.set_state(C.ARM_STATE_DOWN)

        elif new_state == C.ACTION_STATE_MOVE_DUMBBELL:
            self.set_state(C.ARM_STATE_DOWN)

        elif new_state == C.ACTION_STATE_GRAB:
            self.set_state(C.ARM_STATE_GRABBING)

        elif new_state == C.ACTION_STATE_LOCATE_BLOCK:
            self.set_state(C.ARM_STATE_UP)

        elif new_state == C.ACTION_STATE_CENTER_BLOCK:
            self.set_state(C.ARM_STATE_UP)

        elif new_state == C.ACTION_STATE_WAIT_FOR_NUMBER_IMG:
            self.set_state(C.ARM_STATE_UP)

        elif new_state == C.ACTION_STATE_MOVE_BLOCK:
            self.set_state(C.ARM_STATE_UP)

        elif new_state == C.ACTION_STATE_RELEASE:
            self.set_state(C.ARM_STATE_RELEASING)

    def run(self) -> None:
        """
        Listen for incoming messages.
        """
        rospy.spin()


if __name__ == "__main__":
    controller = ArmController()
    controller.run()
