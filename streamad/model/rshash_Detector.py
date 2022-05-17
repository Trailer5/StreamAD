import numpy as np
from streamad.base import BaseDetector
from streamad.util import StreamStatistic
from collections import deque


class RShashDetector(BaseDetector):
    def __init__(
        self,
        init_len: int = 150,
        decay=0.015,
        components_num=100,
        hash_num: int = 10,
    ):
        """Multivariate RSHashDetector :cite:`DBLP:conf/icdm/SatheA16`.

        Args:
            init_len (int, optional): Length of data to burn in/init. Defaults to 150.
            decay (float, optional): Decay ratio. Defaults to 0.015.
            components_num (int, optional): Number of components. Defaults to 100.
            hash_num (int, optional): Number of hash functions. Defaults to 10.
        """
        super().__init__()

        self.buffer = deque(maxlen=init_len)
        self.decay = decay
        self.data_stats = StreamStatistic()
        self.score_stats = StreamStatistic()
        self.hash_num = hash_num
        self.components_num = components_num
        self.cmsketches = [{} for _ in range(hash_num)]

        self.alpha = None
        self.index = -1
        self.effective_s = max(1000, 1.0 / (1 - np.power(2, -self.decay)))
        self.f = np.random.uniform(
            low=1.0 / np.sqrt(self.effective_s),
            high=1 - (1.0 / np.sqrt(self.effective_s)),
            size=self.components_num,
        )

    def _burn_in(self):

        # Normalized the init data
        buffer = np.array(self.buffer)
        buffer_normalized = np.divide(
            buffer - self.data_stats.get_min(),
            self.data_stats.get_max() - self.data_stats.get_min(),
            out=np.zeros_like(buffer),
            where=self.data_stats.get_max() - self.data_stats.get_min() != 0,
        )
        buffer_normalized[np.abs(buffer_normalized) == np.inf] = 0

        for r in range(self.components_num):
            for i in range(buffer.shape[0]):
                Y = np.floor(
                    (buffer_normalized[i, :] + np.array(self.alpha[r]))
                    / self.f[r]
                )

                mod_entry = np.insert(Y, 0, r)
                mod_entry = tuple(mod_entry.astype(int))

                for w in range(self.hash_num):
                    try:
                        value = self.cmsketches[w][mod_entry]
                    except KeyError:
                        value = (0, 0)

                    value = (0, value[1] + 1)
                    self.cmsketches[w][mod_entry] = value

    def fit(self, X):

        if self.index == -1:
            self.alpha = [
                np.random.uniform(low=0, high=self.f[r], size=len(X))
                for r in range(self.components_num)
            ]

        self.index += 1
        self.data_stats.update(X)

        if len(self.buffer) < self.buffer.maxlen:
            self.buffer.append(X)
            return self

        if self.index == self.buffer.maxlen - 1:
            self._burn_in()

        return self

    def score(self, X):

        if len(self.buffer) < self.buffer.maxlen:
            return None

        X_normalized = np.divide(
            X - self.data_stats.get_min(),
            self.data_stats.get_max() - self.data_stats.get_min(),
            out=np.zeros_like(X),
            where=self.data_stats.get_max() - self.data_stats.get_min() != 0,
        )
        X_normalized[np.abs(X_normalized) == np.inf] = 0

        score_instance = 0

        for r in range(self.components_num):
            Y = np.floor((X_normalized + np.array(self.alpha[r])) / self.f[r])
            mod_entry = np.insert(Y, 0, r)
            mod_entry = tuple(mod_entry.astype(int))

            c = []

            for w in range(len(self.cmsketches)):
                try:
                    value = self.cmsketches[w][mod_entry]
                except KeyError:
                    value = (self.index, 0)

                tstamp = value[0]
                wt = value[1]
                new_wt = wt * np.power(2, -self.decay * (self.index - tstamp))
                c.append(new_wt)
                new_tstamp = self.index
                self.cmsketches[w][mod_entry] = (new_tstamp, new_wt + 1)

            min_c = min(c)
            c = np.log(1 + min_c)
            score_instance += c

        score = score_instance / self.components_num

        self.score_stats.update(score)

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