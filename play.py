import argparse
import os
import pickle
import sys
import matplotlib.pylab as plt

from agent import Qlearner
from teacher import Teacher
from game_logic import Game


def plot_agent_reward(rewards):
    """
    Function to plot agent's accumulated reward vs. iteration.
    """
    # Calculate cumulative sum manually
    cumulative_rewards = []
    total = 0
    for reward in rewards:
        total += reward
        cumulative_rewards.append(total)

    # Plot the cumulative rewards
    plt.plot(cumulative_rewards)
    plt.title("Agent Cumulative Reward vs. Iteration")
    plt.ylabel("Reward")
    plt.xlabel("Episode")
    plt.show()


class GameLearning:
    """
    A class that holds the state of the learning process. Learning
    agents are created/loaded here, and a count is kept of the
    games that have been played.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command line arguments.
    alpha : float, optional
        Learning rate for the Q-learning agent (default is 0.5).
    gamma : float, optional
        Discount factor for the Q-learning agent (default is 0.9).
    epsilon : float, optional
        Exploration rate for the Q-learning agent (default is 0.1).
    """

    def __init__(self, args, alpha=0.5, gamma=0.9, epsilon=0.1):
        self.games_played = 0
        self.agent_path = "./trained_agent.pkl"

        if args.load:
            # Load agent
            try:
                with open(self.agent_path, "rb") as f:
                    self.agent = pickle.load(f)
            except IOError:
                print("The agent file does not exist. Quitting.")
                sys.exit(0)

            # If plotting, show plot and quit
            if args.plot:
                plot_agent_reward(self.agent.rewards)
                sys.exit(0)
        else:
            # Check if agent state file already exists, and ask user whether to overwrite if so
            if os.path.isfile(self.agent_path):
                while True:
                    response = input(
                        "An agent state is already saved for this type. "
                        "Are you sure you want to overwrite? [y/n]: "
                    )
                    if response.lower() in ["y", "yes"]:
                        break
                    elif response.lower() in ["n", "no"]:
                        print("OK. Quitting.")
                        sys.exit(0)
                    else:
                        print("Invalid input. Please choose 'y' or 'n'.")

            # Initialize new agent
            self.agent = Qlearner(alpha, gamma, epsilon)

    def beginPlaying(self):
        """
        Loop through game iterations with a human player.
        """
        print("Welcome to Tic-Tac-Toe. You are 'X' and the computer is 'O'.")

        def play_again():
            print("Games played: %i" % self.games_played)
            while True:
                play = input("Do you want to play again? [y/n]: ")
                if play.lower() in ["y", "yes"]:
                    return True
                elif play.lower() in ["n", "no"]:
                    return False
                else:
                    print("Invalid input. Please choose 'y' or 'n'.")

        while True:
            game = Game(self.agent)
            game.start()
            self.games_played += 1
            if not play_again():
                print("OK. Quitting.")
                break

    def beginTeaching(self, episodes):
        """
        Loop through game iterations with a teaching agent.
        """
        teacher = Teacher()
        # Train for allotted number of episodes
        while self.games_played < episodes:
            game = Game(self.agent, teacher=teacher)
            game.start()
            self.games_played += 1

            # Monitor progress
            if self.games_played % 1000 == 0:
                print("Games played: %i" % self.games_played)

        plot_agent_reward(self.agent.rewards)
        self.agent.save_agent(self.agent_path)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Play Tic-Tac-Toe.")
    parser.add_argument(
        "-l", "--load", action="store_true", help="whether to load trained agent"
    )
    parser.add_argument(
        "-t",
        "--teacher_episodes",
        default=None,
        type=int,
        help="employ teacher agent who knows the optimal strategy and will play for TEACHER_EPISODES games",
    )
    parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="whether to plot reward vs. episode of stored agent and quit",
    )
    args = parser.parse_args()

    if args.plot:
        assert args.load, "Must load an agent to plot reward."
        assert (
            args.teacher_episodes is None
        ), "Cannot plot and teach concurrently; must choose one or the other."

    gl = GameLearning(args)
    if args.teacher_episodes is not None:
        gl.beginTeaching(args.teacher_episodes)
    else:
        gl.beginPlaying()
