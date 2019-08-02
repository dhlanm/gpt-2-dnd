import numpy as np
import random
from gpt_2_simple.src.load_dataset import binary_search

class BiasedSampler(object):
    """Samples a slice from an array of sets of variable sized chunks.
    Chooses which set to choose from from a given distribution, then chooses the slice fairly
    from that set of chunks. 

    'Fairly' means that the distribution is the same as sampling from one concatenated chunk,
    but without crossing chunk boundaries."""

    def __init__(self, chunksets, probs = []):
        if not probs: 
            self.probs = [1/len(chunksets) for i in range(len(chunksets))]
        else: 
            self.probs = probs
        assert len(probs) == len(chunksets), f"prob length {len(probs)} does not match chunkset length {len(chunksets)}"
        self.chunksets = chunksets
        self.total_sizes = [sum(chunk.shape[0] for chunk in chunks) for chunks in chunksets]
        self.boundaries = [[0] for i in range(len(chunksets))]
        for i, chunks in enumerate(chunksets):
            for j in range(len(chunks)):
                self.boundaries[i].append(self.boundaries[i][-1] + chunks[j].shape[0])

    def sample(self, length):
        #for consistencies sake, if the length is too much for any chunkset it's too long for all
        assert all([length < self.total_sizes[i] // len(self.chunksets[i]) 
            for i in range(
                len(self.total_sizes)
            )]), "Dataset files are too small to sample {} tokens at a time".format(length)

        chunk_i = np.random.choice(len(self.chunksets), 1, self.probs)[0]
        while True:
            index = random.randint(0, self.total_sizes[chunk_i] - length - 1)
            print(self.boundaries)
            print(chunk_i)
            i = binary_search(lambda j: self.boundaries[chunk_i][j] > index, 0,
                              len(self.boundaries[chunk_i]) - 1) - 1
            if self.boundaries[chunk_i][i + 1] > index + length:
                within_chunk = index - self.boundaries[chunk_i][i]
                return self.chunksets[chunk_i][i][within_chunk:within_chunk + length]
