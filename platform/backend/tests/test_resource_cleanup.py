"""Regression tests for resources that must not outlive their request or run.

These cover the leak fixes: background task references, scheduler shutdown,
and the exercise-tester event cursor (which must not re-parse the whole
journal on every poll).
"""

import asyncio

import app.routers.exercise_tester as exercise_tester
import app.routers.labs as labs
import app.services.scheduler as scheduler


def test_event_cursor_returns_only_new_events(tmp_path, monkeypatch):
    monkeypatch.setattr(exercise_tester, "_RUN_DIR", str(tmp_path))

    for index in range(5):
        exercise_tester._run_append_event("run1", {"n": index})

    events, total = exercise_tester._run_read_events("run1")
    assert [e["n"] for e in events] == [0, 1, 2, 3, 4]
    assert total == 5

    events, total = exercise_tester._run_read_events("run1", after=3)
    assert [e["n"] for e in events] == [3, 4]
    assert total == 5

    events, total = exercise_tester._run_read_events("run1", after=99)
    assert events == []
    assert total == 5

    events, total = exercise_tester._run_read_events("missing")
    assert events == []
    assert total == 0


def test_background_task_reference_is_released():
    async def main():
        async def noop():
            await asyncio.sleep(0)

        task = labs._track_background_task(noop())
        await task
        # Let the done callback run on the next loop iteration.
        await asyncio.sleep(0)
        return len(labs._background_tasks)

    assert asyncio.run(main()) == 0


def test_scheduler_shutdown_cancels_and_awaits_tasks():
    async def main():
        running = asyncio.create_task(asyncio.sleep(3600))
        scheduler._session_cleanup_task = running

        await scheduler.shutdown_scheduler()

        return running.cancelled(), scheduler._session_cleanup_task

    cancelled, tracked = asyncio.run(main())
    assert cancelled is True
    assert tracked is None
