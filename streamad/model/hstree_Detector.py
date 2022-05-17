import numpy as np
from streamad.base import BaseDetector
from streamad.util import StreamStatistic


class Leaf:
    def __init__(
        self,
        left=None,
        right=None,
        r=0,
        l=0,
        split_attrib=0,
        split_value=0.0,
        depth=0,
    ):
        self.left = left
        self.right = right
        self.r = r
        self.l = l
        self.split_attrib = split_attrib
        self.split_value = split_value
        self.k = depth


class HSTreeDetector(BaseDetector):
    def __init__(
        self, window_len: int = 20, tree_height: int = 15, tree_num: int = 100,
    ):
        """Half space tree detectors. :cite:`DBLP:conf/ijcai/TanTL11`.

        Args:
            window_len (int, optional): _description_. Defaults to 20.
            tree_height (int, optional): _description_. Defaults to 15.
            tree_num (int, optional): _description_. Defaults to 100.
        """
        super().__init__()

        self.index = -1
        self.window_len = window_len
        self.tree_height = tree_height
        self.tree_num = tree_num
        self.forest = []
        self.data_stats = StreamStatistic()
        self.score_stats = StreamStatistic()
        self.dimensions = None

    def _generate_max_min(self):
        max_arr = np.zeros(self.dimensions)
        min_arr = np.zeros(self.dimensions)
        for q in range(self.dimensions):
            s_q = np.random.random_sample()
            max_value = max(s_q, 1 - s_q)
            max_arr[q] = s_q + 2 * max_value
            min_arr[q] = s_q - 2 * max_value

        return max_arr, min_arr

    def _init_a_tree(self, max_arr, min_arr, k):
        if k == self.tree_height:
            return Leaf(depth=k)

        leaf = Leaf()
        q = np.random.randint(self.dimensions)
        p = (max_arr[q] + min_arr[q]) / 2.0
        temp = max_arr[q]
        max_arr[q] = p
        leaf.left = self._init_a_tree(max_arr, min_arr, k + 1)
        max_arr[q] = temp
        min_arr[q] = p
        leaf.right = self._init_a_tree(max_arr, min_arr, k + 1)
        leaf.split_attrib = q
        leaf.split_value = p
        leaf.k = k
        return leaf

    def _update_tree_mass(self, tree, X, is_ref_window):
        if tree:
            if tree.k != 0:
                if is_ref_window:
                    tree.r += 1
                else:
                    tree.l += 1
            if X[tree.split_attrib] > tree.split_value:
                tree_new = tree.right
            else:
                tree_new = tree.left
            self._update_tree_mass(tree_new, X, is_ref_window)

    def _reset_tree(self, tree):
        if tree:
            tree.r = tree.l
            tree.l = 0
            self._reset_tree(tree.left)
            self._reset_tree(tree.right)

    def fit(self, X: np.ndarray) -> None:
        self.index += 1
        self.data_stats.update(X)

        self.X_normalized = np.divide(
            X - self.data_stats.get_min(),
            self.data_stats.get_max() - self.data_stats.get_min(),
            out=np.zeros_like(X),
            where=self.data_stats.get_max() - self.data_stats.get_min() != 0,
        )
        self.X_normalized[np.abs(self.X_normalized) == np.inf] = 0

        if self.dimensions is None:
            self.dimensions = len(X)
            max_arr, min_arr = self._generate_max_min()
            tree = self._init_a_tree(max_arr, min_arr, 0)
            self.forest.append(tree)

        if self.index < self.window_len:
            for tree in self.forest:
                self._update_tree_mass(tree, X, True)
        elif self.index > self.window_len and self.index % self.window_len == 0:
            for tree in self.forest:
                self._reset_tree(tree)

        return self

    def score(self, X: np.ndarray) -> float:

        if self.index < self.window_len:
            return None

        score = 0.0

        for tree in self.forest:
            score += self._score_tree(tree, self.X_normalized, 0)
            self._update_tree_mass(tree, self.X_normalized, False)

        self.score_stats.update(score / len(self.forest))

        score_mean = self.score_stats.get_mean()
        score_std = self.score_stats.get_std()
        z_score = np.divide(
            (score - score_mean),
            score_std,
            out=np.zeros_like(score),
            where=score_std != 0,
        )
        if z_score > 3:
            max_score = self.score_stats.get_max()
            score = (score - score_mean) / (max_score - score_mean)
        elif z_score < -3:
            min_score = self.score_stats.get_min()
            score = (score - score_mean) / (min_score - score_mean)
        else:
            return 0
        return score

    def _score_tree(self, tree, X, k):
        s = 0
        if not tree:
            return s

        s += tree.r * (2 ** k)

        if X[tree.split_attrib] > tree.split_value:
            tree_new = tree.right
        else:
            tree_new = tree.left

        s += self._score_tree(tree_new, X, k + 1)

        return s