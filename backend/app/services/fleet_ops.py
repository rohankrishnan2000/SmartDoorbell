from backend.app.models.domain import Device, EdgeCommand


class FleetCommandCenter:
    allowed_commands = {
        "reboot",
        "rotate_certificate",
        "pull_diagnostics",
        "update_model",
        "set_roi",
        "clear_local_cache",
    }

    def queue_command(
        self,
        device: Device,
        command_type: str,
        payload: dict,
        issued_by: str,
    ) -> EdgeCommand:
        if command_type not in self.allowed_commands:
            raise ValueError(f"Unsupported edge command {command_type}")
        return EdgeCommand(
            device_id=device.id,
            command_type=command_type,
            payload=payload,
            issued_by=issued_by,
            status="queued",
        )

