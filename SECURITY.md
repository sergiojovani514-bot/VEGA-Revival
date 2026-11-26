# Security Policy

## Scope

This candidate contains a local Vulkan compute smoke test. It is not a driver, privileged service, network service, or production inference runtime.

## Reporting

Do not publish secrets, personal data, proprietary driver material, or raw memory dumps in an issue. Contact the repository maintainers privately through GitHub's security advisory or contact mechanism, include a concise impact description and safe reproduction steps, and redact machine identifiers and paths.

## Safe use

Use a vendor-supported Vulkan driver. Do not disable thermal protections, alter firmware or voltage, or modify a system driver. Stop if the GPU or system reports an error or unsafe temperature. The included smoke test is short; extended stress testing is out of scope.
