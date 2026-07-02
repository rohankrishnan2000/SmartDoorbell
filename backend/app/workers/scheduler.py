from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Callable


class JobCadence(StrEnum):
    EVERY_MINUTE = "every_minute"
    HOURLY = "hourly"
    NIGHTLY = "nightly"
    WEEKLY = "weekly"


@dataclass(frozen=True)
class ScheduledJob:
    name: str
    cadence: JobCadence
    queue: str
    timeout_seconds: int
    max_retries: int
    owner: str


@dataclass(frozen=True)
class JobExecutionPlan:
    job_name: str
    run_at: datetime
    lock_key: str
    idempotency_key: str
    payload: dict


class WorkerScheduler:
    jobs = [
        ScheduledJob("edge-heartbeat-sweeper", JobCadence.EVERY_MINUTE, "ops", 30, 3, "device-platform"),
        ScheduledJob("webhook-retry-drainer", JobCadence.EVERY_MINUTE, "notifications", 45, 5, "growth-platform"),
        ScheduledJob("slo-burn-rate-calculator", JobCadence.HOURLY, "ops", 120, 2, "infra"),
        ScheduledJob("nightly-media-retention", JobCadence.NIGHTLY, "privacy", 1800, 1, "privacy"),
        ScheduledJob("label-export-to-training", JobCadence.NIGHTLY, "mlops", 900, 2, "ml-platform"),
        ScheduledJob("device-cert-expiry-scan", JobCadence.NIGHTLY, "security", 300, 2, "security"),
        ScheduledJob("weekly-model-drift-report", JobCadence.WEEKLY, "mlops", 3600, 1, "ml-platform"),
    ]

    def due_jobs(self, now: datetime | None = None) -> list[JobExecutionPlan]:
        now = now or datetime.now(UTC)
        plans: list[JobExecutionPlan] = []
        for job in self.jobs:
            if self._is_due(job, now):
                plans.append(
                    JobExecutionPlan(
                        job_name=job.name,
                        run_at=now,
                        lock_key=f"job-lock:{job.name}",
                        idempotency_key=f"{job.name}:{now.strftime('%Y%m%d%H')}",
                        payload={"queue": job.queue, "owner": job.owner, "timeout_seconds": job.timeout_seconds},
                    )
                )
        return plans

    def _is_due(self, job: ScheduledJob, now: datetime) -> bool:
        if job.cadence == JobCadence.EVERY_MINUTE:
            return True
        if job.cadence == JobCadence.HOURLY:
            return now.minute == 0
        if job.cadence == JobCadence.NIGHTLY:
            return now.hour == 2 and now.minute == 0
        if job.cadence == JobCadence.WEEKLY:
            return now.weekday() == 0 and now.hour == 3 and now.minute == 0
        return False


class WorkerRegistry:
    def __init__(self) -> None:
        self.handlers: dict[str, Callable[[dict], dict]] = {}

    def register(self, job_name: str, handler: Callable[[dict], dict]) -> None:
        self.handlers[job_name] = handler

    def run(self, plan: JobExecutionPlan) -> dict:
        handler = self.handlers.get(plan.job_name)
        if not handler:
            return {"status": "skipped", "reason": "No handler registered", "job": plan.job_name}
        return {"status": "completed", "job": plan.job_name, "result": handler(plan.payload)}

