from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class MeterName(StrEnum):
    EVENT_INGEST = "event_ingest"
    MEDIA_MINUTES = "media_minutes"
    MODEL_INFERENCE = "model_inference"
    LOCK_COMMAND = "lock_command"
    WEBHOOK_DELIVERY = "webhook_delivery"
    AGENT_REVIEW = "agent_review"


@dataclass(frozen=True)
class PlanLimit:
    meter: MeterName
    included: int
    hard_limit: int
    overage_unit_price_cents: int


@dataclass
class UsageEvent:
    organization_id: str
    meter: MeterName
    quantity: int
    source: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    dimensions: dict = field(default_factory=dict)


@dataclass(frozen=True)
class QuotaDecision:
    accepted: bool
    meter: MeterName
    projected_usage: int
    hard_limit: int
    billable_overage: int
    reason: str


class UsageMeter:
    default_limits = {
        MeterName.EVENT_INGEST: PlanLimit(MeterName.EVENT_INGEST, 100_000, 250_000, 1),
        MeterName.MEDIA_MINUTES: PlanLimit(MeterName.MEDIA_MINUTES, 2_000, 5_000, 4),
        MeterName.MODEL_INFERENCE: PlanLimit(MeterName.MODEL_INFERENCE, 500_000, 2_000_000, 1),
        MeterName.LOCK_COMMAND: PlanLimit(MeterName.LOCK_COMMAND, 10_000, 25_000, 2),
        MeterName.WEBHOOK_DELIVERY: PlanLimit(MeterName.WEBHOOK_DELIVERY, 50_000, 150_000, 1),
        MeterName.AGENT_REVIEW: PlanLimit(MeterName.AGENT_REVIEW, 5_000, 20_000, 10),
    }

    def project(self, meter: MeterName, current_usage: int, increment: int) -> QuotaDecision:
        limit = self.default_limits[meter]
        projected = current_usage + increment
        overage = max(0, projected - limit.included)
        if projected > limit.hard_limit:
            return QuotaDecision(
                accepted=False,
                meter=meter,
                projected_usage=projected,
                hard_limit=limit.hard_limit,
                billable_overage=overage,
                reason=f"{meter.value} would exceed hard limit.",
            )
        return QuotaDecision(
            accepted=True,
            meter=meter,
            projected_usage=projected,
            hard_limit=limit.hard_limit,
            billable_overage=overage,
            reason="Usage accepted within plan guardrails.",
        )

    def invoice_preview(self, usage: dict[MeterName, int]) -> dict:
        line_items = []
        total_cents = 0
        for meter, quantity in usage.items():
            limit = self.default_limits[meter]
            overage = max(0, quantity - limit.included)
            subtotal = overage * limit.overage_unit_price_cents
            total_cents += subtotal
            line_items.append(
                {
                    "meter": meter.value,
                    "quantity": quantity,
                    "included": limit.included,
                    "overage": overage,
                    "unit_price_cents": limit.overage_unit_price_cents,
                    "subtotal_cents": subtotal,
                }
            )
        return {"currency": "USD", "total_cents": total_cents, "line_items": line_items}

