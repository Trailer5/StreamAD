from streamad.util import StreamGenerator, UnivariateDS, MultivariateDS
from streamad.model import LodaDetector


def test_score():
    ds = UnivariateDS()
    stream = StreamGenerator(ds.data)
    detector = LodaDetector()
    for x in stream.iter_item():
        score = detector.fit_score(x)

        if score is not None:
            assert type(score) is float


def test_multi_score():
    ds = MultivariateDS()
    stream = StreamGenerator(ds.data)
    detector = LodaDetector()
    for x in stream.iter_item():
        score = detector.fit_score(x)

        if score is not None:
            assert type(score) is float
