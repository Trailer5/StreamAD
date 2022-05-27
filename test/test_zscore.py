from streamad.util import StreamGenerator, UnivariateDS
from streamad.model import ZScoreDetector


def test_score():
    ds = UnivariateDS()
    stream = StreamGenerator(ds.data)
    detector = ZScoreDetector()
    for x in stream.iter_item():
        score = detector.fit_score(x)

        if score is not None:
            assert type(score) is float
