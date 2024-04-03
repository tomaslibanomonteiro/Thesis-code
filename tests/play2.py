
from pymoo.util.ref_dirs.energy import RieszEnergyReferenceDirectionFactory
from pymoo.util.ref_dirs.energy_layer import \
    LayerwiseRieszEnergyReferenceDirectionFactory
from pymoo.util.ref_dirs.reduction import \
    ReductionBasedReferenceDirectionFactory
from pymoo.util.reference_direction import MultiLayerReferenceDirectionFactory

from pymoo.util.reference_direction import UniformReferenceDirectionFactory
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.visualization.scatter import Scatter

# ref_dirs = get_reference_directions(
#     "multi-layer",
#     get_reference_directions("das-dennis", 3, n_partitions=2, scaling=1.0),
#     get_reference_directions("das-dennis", 3, n_partitions=1, scaling=0.5)
# )

# Scatter().add(ref_dirs).show()

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
        else:
            raise Exception("Not implemented for more than 15 objectives.")
        
        self.add_layer(layer_1)
        if layer_2 is not None:
            self.add_layer(layer_2)
        
ref_dirs = MyLayers(6).do() 

# layer_1 = UniformReferenceDirectionFactory(6, n_partitions=2, scaling=0.5).do()
# layer_2 = UniformReferenceDirectionFactory(6, n_partitions=3, scaling=1).do()

# # ref_dirs = MultiLayerReferenceDirectionFactory(layer_1, layer_2)
# ref_dirs = MultiLayerReferenceDirectionFactory()
# ref_dirs.add_layer(layer_1)
# ref_dirs.add_layer(layer_2)
# ref_dirs = ref_dirs.do()


algorithm = MOEAD(ref_dirs=ref_dirs)
print(algorithm)