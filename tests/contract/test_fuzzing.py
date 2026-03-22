import schemathesis
from hypothesis import settings

from app.main import app

# FastAPI defaults to OpenAPI 3.1.0, which breaks current Schemathesis parser
app.openapi_version = "3.0.2"

schema = schemathesis.from_asgi("/openapi.json", app)


@schema.parametrize()
@settings(max_examples=100, deadline=None)
def test_openapi_fuzzing(case: schemathesis.models.Case) -> None:
    """
    Fuzzes all OpenAPI endpoints to ensure contract compliance and 5xx absence.
    """
    response = case.call()  # Using the modern unified call API
    case.validate_response(response)
