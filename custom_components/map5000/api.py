import asyncio
import json
import logging
import re

_LOGGER = logging.getLogger(__name__)


class Map5000Api:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.subscription_url = None
        self.process = None

    async def _curl(self, method, path, payload=None, timeout=70):
        args = [
            "curl",
            "-k",
            "-sS",
            "--digest",
            "-u",
            f"{self.username}:{self.password}",
            "--max-time",
            str(timeout),
            "-H",
            "Accept: application/json",
        ]

        if method == "POST":
            args += [
                "-H",
                "Content-Type: application/json",
                "-X",
                "POST",
                "-d",
                json.dumps(payload),
            ]

        args.append(f"https://{self.host}{path}")

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(
                f"curl failed ({proc.returncode}): "
                f"{stderr.decode(errors='replace')}"
            )

        text = stdout.decode().strip()

        if not text:
            return {}

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"response": text}

    async def get_point(self, point_url):
        return await self._curl("GET", point_url, timeout=10)

    async def create_subscription(self, point_urls):
        data = await self._curl(
            "POST",
            "/sub",
            {
                "@cmd": "SUBSCRIBE",
                "bufferSize": 100,
                "leaseTime": 600,
                "subscriptions": [
                    {
                        "eventType": ["CHANGED"],
                        "urls": point_urls,
                    }
                ],
            },
            timeout=10,
        )

        self.subscription_url = data["subscriptionURL"]
        _LOGGER.info(
            "MAP5000 subscription created: %s",
            self.subscription_url,
        )
        return data

    async def fetch_events(self):
        if not self.subscription_url:
            raise RuntimeError("No MAP5000 subscription")

        return await self._curl(
            "POST",
            self.subscription_url,
            {
                "@cmd": "FETCHEVENTS",
                "maxEvents": 100,
                "minEvents": 1,
                "maxTime": 60,
            },
            timeout=70,
        )

    async def get_incident(self, incident_url):
        """MAP5000-Incident direkt abrufen."""
        return await self._curl("GET", incident_url, timeout=10)


    async def silence_incidents(self):
        """Signalgeber aktiver MAP5000-Incidents stummschalten."""
        return await self._curl(
            "POST",
            "/inc",
            payload={"@cmd": "SILENCE"},
            timeout=20,
        )


    async def start_walktest(self):
        """Zentralen MAP5000-Begehtest starten."""
        return await self._curl(
            "POST",
            "/areas",
            payload={
                "@cmd": "STARTWALKTEST",
                "includedPoints": "ALL",
            },
            timeout=20,
        )

    async def stop_walktest(self):
        """Zentralen MAP5000-Begehtest beenden."""
        return await self._curl(
            "POST",
            "/areas",
            payload={"@cmd": "STOPWALKTEST"},
            timeout=20,
        )


    async def handle_incidents(self):
        """Offene MAP5000-Incidents quittieren / behandeln."""
        return await self._curl(
            "POST",
            "/inc",
            payload={"@cmd": "HANDLE"},
            timeout=20,
        )


    async def get_config(self):
        """Komplette MAP5000-Konfiguration abrufen."""
        return await self._curl("GET", "/config", timeout=20)

    async def send_command(self, object_url, command):
        """Befehl an ein MAP5000-Objekt senden."""
        return await self._curl(
            "POST",
            object_url,
            payload={"@cmd": command},
            timeout=20,
        )

    async def arm_area(self, area_url):
        """Bereich sofort ohne Austrittsverzögerung scharfschalten."""
        return await self._curl(
            "POST",
            area_url,
            payload={
                "@cmd": "ARM",
                "bypassOffNormalDevices": False,
                "exitDelay": "ZERO",
            },
            timeout=20,
        )

    async def disarm_area(self, area_url):
        """Bereich unscharfschalten."""
        return await self.send_command(area_url, "DISARM")

    async def disable_point(self, point_url):
        """Melder sperren."""
        return await self.send_command(point_url, "DISABLE")

    async def enable_point(self, point_url):
        """Melder entsperren."""
        return await self.send_command(point_url, "ENABLE")
