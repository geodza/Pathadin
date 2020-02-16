from common_shapely.shapely_utils import ProbablyContainsChecker
from slice.generator.geometry.hook.bb_geometry_probably_contains_hook import BBGeometryProbablyContainsHook
from slice.generator.geometry.patch_geometry_generator_hooks import PatchGeometryGeneratorHooks
from slice.generator.pos.patch_pos_generator import PatchPosGenerator

if __name__ == '__main__':
    roipg = PatchGeometryGeneratorHooks(
        [BBGeometryProbablyContainsHook(ProbablyContainsChecker(512, 512, 1024, 1024))],
        []
    )
    poss = PatchPosGenerator().create((1000, 1000), 256)
    gen = roipg.create(poss, 256)
    print(gen)
    for i in gen:
        print(i)
