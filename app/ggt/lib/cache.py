from datetime import datetime, timedelta
import functools
#import logging


def timed_lru_cache(**timedelta_kwargs):
    def _wrapper(f):
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() + update_delta
        f = functools.lru_cache(None)(f)

        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            nonlocal next_update
            now = datetime.utcnow()
            if now >= next_update:
                f.cache_clear()
                next_update = now + update_delta
                print('⏳ cache miss')
            else:
                print('✅ cache hit!')

            return f(*args, **kwargs)

        return _wrapped

    return _wrapper
