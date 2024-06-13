"""
Algorithm Factory to choose avaiable algorithms
"""
from pkg.edivisive import EDivisive
from pkg.isolationForest import IsolationForestWeightedMean

class AlgorithmFactory: # pylint: disable= too-few-public-methods
    """Algorithm Factory to choose algorithm
    """
    def instantiate_algorithm(self, algorithm, matcher, dataframe, test):
        """Algorithm instantiation method

        Args:
            algorithm (str): Name of the algorithm
            matcher (Matcher): Matcher class
            dataframe (pd.Dataframe): dataframe with data
            test (dict): test information dictionary

        Raises:
            ValueError: When invalid algo is chosen

        Returns:
            Algorithm : Algorithm
        """
        if algorithm == "EDivisive":
            return EDivisive(matcher, dataframe, test)
        if algorithm == "IsolationForest":
            return IsolationForestWeightedMean(matcher, dataframe, test)
        raise ValueError("Invalid algorithm called")
