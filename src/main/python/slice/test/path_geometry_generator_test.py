from common_shapely.shapely_utils import ProbablyContainsChecker
from slice.generator.geometry.hook.bb_geometry_probably_contains_hook import BBGeometryProbablyContainsHook
from slice.generator.geometry.patch_geometry_generator_hooks import PatchGeometryGeneratorHooks
from slice.generator.pos.patch_pos_generator import PatchPosGenerator

if __name__ == '__main__':
    roipg = PatchGeometryGeneratorHooks(
        patch_size=(256, 256),
        bb_hooks=[BBGeometryProbablyContainsHook(ProbablyContainsChecker(512, 512, 1024, 1024))],
        patch_hooks=[]
    )
    poss = PatchPosGenerator((1000, 1000), 256, 256).create()
    gen = roipg.create(poss)
    print(gen)
    for i in gen:
        print(i)
