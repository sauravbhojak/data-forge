"""Time-series correlated analytics dataset generator."""

from __future__ import annotations

import math
import random
from collections.abc import Iterator
from datetime import date, timedelta
from typing import Any

import numpy as np

from app.constants.distributions import AnalyticsDatasetType
from app.schemas.generation import AnalyticsRequest

# Seed for reproducible NumPy arrays (actual random seed is still used per-request)
_RNG_SEED_RANGE = 2**31


class AnalyticsGenerator:
    """
    Generates realistic, correlated time-series analytics datasets.

    Uses NumPy to vectorise trend/seasonality/noise computation then
    yields rows one at a time — no in-memory accumulation.
    """

    def generate(self, request: AnalyticsRequest) -> Iterator[dict[str, Any]]:
        """Dispatch to the appropriate dataset generator."""
        match request.dataset_type:
            case AnalyticsDatasetType.REVENUE:
                yield from self._revenue(request)
            case AnalyticsDatasetType.WEBSITE:
                yield from self._website(request)
            case AnalyticsDatasetType.IOT:
                yield from self._iot(request)
            case AnalyticsDatasetType.VPN:
                yield from self._vpn(request)

    # ── Revenue ───────────────────────────────────────────────────────────────

    def _revenue(self, req: AnalyticsRequest) -> Iterator[dict[str, Any]]:
        n = req.row_count
        rng = np.random.default_rng(random.randint(0, _RNG_SEED_RANGE))
        t = np.arange(n, dtype=float)

        # Trend + weekly seasonality + noise
        trend = (10_000 + 50 * t) * req.trend_strength
        seasonality = 2_000 * np.sin(2 * math.pi * t / 7)
        noise = rng.normal(0, 500 * req.noise_level, n)
        revenue = np.clip(trend + seasonality + noise, 100, None)

        profit_ratio = rng.uniform(0.15, 0.30, n)
        expense_ratio = rng.uniform(0.55, 0.75, n)
        cust_noise = rng.uniform(0.8, 1.2, n)

        profit = np.clip(revenue * profit_ratio, 0, None)
        expenses = np.clip(revenue * expense_ratio, 0, None)
        customer_count = np.clip((revenue / 50 * cust_noise).astype(int), 1, None)

        start = self._parse_start(req.start_date)
        for i in range(n):
            yield {
                "date": (start + timedelta(days=i)).isoformat(),
                "revenue": round(float(revenue[i]), 2),
                "profit": round(float(profit[i]), 2),
                "expenses": round(float(expenses[i]), 2),
                "customer_count": int(customer_count[i]),
            }

    # ── Website Analytics ─────────────────────────────────────────────────────

    def _website(self, req: AnalyticsRequest) -> Iterator[dict[str, Any]]:
        n = req.row_count
        rng = np.random.default_rng(random.randint(0, _RNG_SEED_RANGE))
        t = np.arange(n, dtype=float)

        trend = (5_000 + 30 * t) * req.trend_strength
        seasonality = 800 * np.sin(2 * math.pi * t / 7)
        noise = rng.normal(0, 300 * req.noise_level, n)
        users = np.clip(trend + seasonality + noise, 100, None).astype(int)

        sessions = (users * rng.uniform(1.2, 1.8, n)).astype(int)
        bounce_rate = np.clip(rng.normal(45, 10 * req.noise_level, n), 10, 90)
        conversion_rate = np.clip(rng.normal(3.5, 1.0 * req.noise_level, n), 0.1, 20)
        revenue = np.clip(users * rng.uniform(0.8, 2.5, n), 0, None)

        start = self._parse_start(req.start_date)
        for i in range(n):
            yield {
                "date": (start + timedelta(days=i)).isoformat(),
                "users": int(users[i]),
                "sessions": int(sessions[i]),
                "bounce_rate": round(float(bounce_rate[i]), 2),
                "conversion_rate": round(float(conversion_rate[i]), 2),
                "revenue": round(float(revenue[i]), 2),
            }

    # ── IoT Sensor ────────────────────────────────────────────────────────────

    def _iot(self, req: AnalyticsRequest) -> Iterator[dict[str, Any]]:
        n = req.row_count
        rng = np.random.default_rng(random.randint(0, _RNG_SEED_RANGE))

        # Time-series with diurnal variation
        t = np.linspace(0, 4 * math.pi, n)
        temp = 22 + 8 * np.sin(t / 24) + rng.normal(0, 1.5 * req.noise_level, n)
        humidity = 60 + 15 * np.cos(t / 24) + rng.normal(0, 3 * req.noise_level, n)
        humidity = np.clip(humidity, 0, 100)
        pressure = 1013 + 5 * np.sin(t / 48) + rng.normal(0, 2 * req.noise_level, n)

        device_ids = [f"device_{i % 10 + 1:04d}" for i in range(n)]

        start_dt = self._parse_start(req.start_date)
        for i in range(n):
            ts = start_dt.isoformat() + f"T{(i % 24):02d}:{(i % 60):02d}:00"
            yield {
                "timestamp": ts,
                "device_id": device_ids[i],
                "temperature": round(float(temp[i]), 2),
                "humidity": round(float(humidity[i]), 2),
                "pressure": round(float(pressure[i]), 2),
            }

    # ── VPN Analytics ─────────────────────────────────────────────────────────

    def _vpn(self, req: AnalyticsRequest) -> Iterator[dict[str, Any]]:
        n = req.row_count
        rng = np.random.default_rng(random.randint(0, _RNG_SEED_RANGE))
        t = np.arange(n, dtype=float)

        countries = [
            "United States", "Germany", "United Kingdom", "Japan",
            "Canada", "Australia", "France", "Brazil",
        ]

        trend = (1_000 + 10 * t) * req.trend_strength
        noise = rng.normal(0, 200 * req.noise_level, n)
        active_users = np.clip(trend + noise, 0, None).astype(int)

        bandwidth = np.clip(active_users * rng.uniform(0.1, 0.5, n), 1, None)
        latency = np.clip(rng.normal(40, 15 * req.noise_level, n), 1, 500)
        packet_loss = np.clip(rng.exponential(0.5 * req.noise_level, n), 0, 5)

        start = self._parse_start(req.start_date)
        for i in range(n):
            yield {
                "date": (start + timedelta(days=i % 365)).isoformat(),
                "country": random.choice(countries),
                "active_users": int(active_users[i]),
                "bandwidth_usage_gb": round(float(bandwidth[i]), 2),
                "latency_ms": round(float(latency[i]), 1),
                "packet_loss_pct": round(float(packet_loss[i]), 3),
            }

    @staticmethod
    def _parse_start(start_date: str | None) -> date:
        if start_date:
            try:
                return date.fromisoformat(start_date)
            except ValueError:
                pass
        return date(2024, 1, 1)
