"""
A replacement of ProcessPoolExecutor implemented by Ray

Benefit:
- More suitable for multi-process with higher between-process communication
"""
import ray
from ray.util import ActorPool
import signal
__all__ = ['RayActorPoolExecutor']


@ray.remote
class Actor:
    def func(self, func, input_data):
        result = func(input_data)
        return result


class RayActorPoolExecutor:
    def __init__(self, max_workers=None):
        assert max_workers is not None, 'Please provide max workers count'
        self._max_workers = max_workers
        if self._max_workers > 1:
            self.actor_pool = ActorPool([Actor.remote()] * max_workers)
        # graceful exit: save the dump file
        # signal.signal(signal.SIGINT, self.exit_gracefully)
        # signal.signal(signal.SIGTERM, self.exit_gracefully)

    def map(self, func, input_generator):
        if self._max_workers > 1:
            return self.actor_pool.map_unordered(
                lambda a, input_data: a.func.remote(func, input_data),
                input_generator)
        else:
            return map(func, input_generator)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.exit()

    def exit_gracefully(self, *args):
        self.exit()
        print('[RayActorPoolExecutor] exit gracefully')

    def exit(self):
        if self._max_workers > 1:
            print('RayActorPoolExecutor closed')
            while self.actor_pool.has_free():
                idle_actor = self.actor_pool.pop_idle()
                idle_actor.__ray_terminate__.remote()
