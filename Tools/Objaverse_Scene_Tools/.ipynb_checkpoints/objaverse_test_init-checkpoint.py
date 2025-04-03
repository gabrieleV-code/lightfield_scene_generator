import objaverse
objaverse.__version__

uids = objaverse.load_uids()

annotations = objaverse.load_annotations(uids[:10])
annotations[uids[0]]

import multiprocessing
processes = multiprocessing.cpu_count()
processes

import random

random.seed(42)

uids = objaverse.load_uids()
random_object_uids = random.sample(uids, 10)

random_object_uids