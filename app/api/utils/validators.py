from uuid import UUID


def is_valid_uuid(value):
    try:
        UUID(value)
        return True
    except:
        return False
