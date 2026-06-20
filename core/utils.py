import uuid


def generate_unique_id(prefix: str, model, field: str = 'student_id', length: int = 8) -> str:
    """Generate a unique human-readable ID like STU-A1B2C3D4."""
    for _ in range(50):
        code = f'{prefix}-{uuid.uuid4().hex[:length].upper()}'
        if not model.objects.filter(**{field: code}).exists():
            return code
    return f'{prefix}-{uuid.uuid4().hex.upper()}'
