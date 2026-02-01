import random
from typing import Dict, Deque
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.history: Dict[str, Deque[float]] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Видаляє застарілі timestamps (старіші за current_time - window_size).
        Якщо після очищення deque порожній — видаляє користувача зі структури.
        """
        if user_id not in self.history:
            return

        q = self.history[user_id]
        boundary = current_time - self.window_size

        while q and q[0] <= boundary:
            q.popleft()

        if not q:
            del self.history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        True, якщо в поточному sliding window кількість повідомлень < max_requests.
        Перше повідомлення завжди дозволене.
        """
        now = time.time()
        self._cleanup_window(user_id, now)

        if user_id not in self.history:
            return True

        return len(self.history[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """
        Якщо можна — записує timestamp і повертає True.
        Якщо не можна — не записує і повертає False.
        """
        now = time.time()
        self._cleanup_window(user_id, now)

        if user_id in self.history and len(self.history[user_id]) >= self.max_requests:
            return False

        if user_id not in self.history:
            self.history[user_id] = deque()
        self.history[user_id].append(now)
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        now = time.time()
        self._cleanup_window(user_id, now)

        if user_id not in self.history:
            return 0.0

        q = self.history[user_id]

        if len(q) < self.max_requests:
            return 0.0

        oldest = q[0]
        allowed_at = oldest + self.window_size
        wait = allowed_at - now
        return max(0.0, wait)


def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
