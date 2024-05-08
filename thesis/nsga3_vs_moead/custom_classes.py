from pymoo.termination.max_gen import MaximumGenerationTermination

class MyNumGen(MaximumGenerationTermination):
    def __init__(self, prob_id='prob_id(convert)', **kwargs):
        if 'dtlz1' in prob_id:
            n_gen = 400
        elif 'dtlz2' in prob_id:
            n_gen = 250
        elif 'dtlz3' in prob_id:
            n_gen = 1000
        elif 'dtlz4' in prob_id:
            n_gen = 600
        else:
            raise Exception("Problem id must be 'dtlz1', 'dtlz2', 'dtlz3' or 'dtlz4'")
        super().__init__(n_gen, **kwargs)

from pymoo.util.reference_direction import MultiLayerReferenceDirectionFactory, UniformReferenceDirectionFactory

class MyLayers(MultiLayerReferenceDirectionFactory):
    def __init__(self, n_dim: int):
        super().__init__()
        
        layer_2 = None
        if n_dim == 2:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=99).do()
        elif n_dim == 3:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=12).do()
        elif n_dim in [4,5]:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=6).do()
        elif n_dim in [6,7,8,9,10]:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=2, scaling=0.5).do()
            layer_2 = UniformReferenceDirectionFactory(n_dim, n_partitions=3, scaling=1).do()
        elif n_dim in [11,12,13,14,15]:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=1, scaling=0.5).do()
            layer_2 = UniformReferenceDirectionFactory(n_dim, n_partitions=2, scaling=1).do()
        elif not isinstance(n_dim, int):
            raise Exception("n_dim must be an integer.")
        elif n_dim > 15 or n_dim < 2:
            raise Exception("Not implemented for n_dim > 15 or n_dim < 2.")
        
        self.add_layer(layer_1)
        if layer_2 is not None:
            self.add_layer(layer_2)
