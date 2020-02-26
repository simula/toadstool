
from random import randint

stage_order = [
    (1,1),
    (1,2),
    (1,3),
    (2,2),
    (1,4),
    (3,1),
    (4,1),
    (2,1),
    (2,3),
    (2,4),
    (3,2),
    (3,3),
    (3,4),
    (4,2)
]

stage_order_len = len(stage_order)

def make_next_stage(world, stage, num):
    base = 'SuperMarioBros-'
    tail = '-v0'

    if num < stage_order_len:
        world = stage_order[num][0]
        stage = stage_order[num][1]
    else:
        if stage >= 4:
            stage = 1

            if world >= 8:
                world = 1
            else:
                world += 1
        else:
            stage += 1
    new_world = base + str(world) + '-' + str(stage) + tail

    return world, stage, new_world

def make_random_stage():
    base = 'SuperMarioBros-'
    tail = '-v0'
    world = str(randint(1,8))
    stage = str(randint(1,4))
    new_world = base + world + '-' + stage + tail

    return new_world