#!/usr/bin/env python

import random
import requests

__author__ = 'brent'


class IndexedArm(object):
    def __init__(self, index, count=0, average_reward=0.):
        self.index = index
        self.count = count
        self.average_reward = float(average_reward)

    def update(self, reward):
        self.average_reward = (self.count * self.average_reward + reward) / (self.count + 1)
        self.count += 1


def accumulate(values):
    """
    Given an iterable yields sum total of the list at each iteration
    :param values: an iterable whose elements can be added
    :yields: accumulated subtotals for each element
    :return: None
    """
    # TODO: replace usage with numpy.cumsum(values) after adding numpy
    accumulation = 0
    for value in values:
        accumulation += value
        yield accumulation


class MultiArmedBandit(object):
    def __init__(self, number_arms=0):
        self.arms = [IndexedArm(index=i) for i in range(number_arms)]
        self.total_reward = 0

    @property
    def best_arm(self):
        return max(self.arms, key=lambda x: x.average_reward)

    def update(self, arm, reward):
        arm.update(reward)
        self.total_reward += reward


class EpsilonGreedyBandit(MultiArmedBandit):

    def __init__(self, number_arms=0, epsilon=0.20):
        super(EpsilonGreedyBandit, self).__init__(number_arms)

        self.epsilon = epsilon
        if self.epsilon < 0. or self.epsilon > 1.:
            raise ValueError("self.epsilon should be a decimal between 0.0 and 1.0, received {0}".format(self.epsilon))

    def select_arm(self):
        if random.random() > self.epsilon:
            return self.best_arm
        else:
            return random.choice(self.arms)

    def probability_distribution(self):
        """
        This function returns the probability of each arm being choosen
        :return: an array of tuples [(<probability to choose this arm>, <the arm class>), ...]
        """
        if not len(self.arms):
            return []

        possibility_of_pulling_others = self.epsilon / len(self.arms)
        possibility_of_pulling_best_arm = 1 - self.epsilon + possibility_of_pulling_others

        def arm_probability(arm):
            if arm != self.best_arm:
                return possibility_of_pulling_others
            else:
                return possibility_of_pulling_best_arm

        return [arm_probability(arm) for arm in self.arms]

    def cumulative_probability_distribution(self):
        """
        Returns the cumulative probability distribution for the bandit's arms
        :return: list of cumulative probabilities in the same order as this bandit's arms
        """
        return list(accumulate(self.probability_distribution()))


def main():
    bandit = EpsilonGreedyBandit(number_arms=10, epsilon=0.20)

    for i in range(100):
        arm = bandit.select_arm()

        url_template = 'http://bandit-server.elasticbeanstalk.com/{type}?k={arm}&u={username}'
        url = url_template.format(type="0", arm=arm.index, username="Isla")
        r = requests.get(url)

        reward = float(r.text)
        bandit.update(arm, reward)

    print bandit.probability_distribution(), bandit.total_reward


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print ''
