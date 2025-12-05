from typing import List, Optional
from strawberry.extensions import SchemaExtension
from strawberry.types import ExecutionContext
from graphql import GraphQLError

from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig
from treasury.services.gateways.ttb_api.main.application.exceptions.exceptions import GenericException, \
    UnauthorizedException, ForbiddenException, InternalServerException, ServiceUnavailableException, \
    RateLimitExceededException, BadRequestException, NotFoundException

logger = GlobalConfig.get_logger(__name__)


class ErrorHandlerExtension(SchemaExtension):
    """Strawberry extension for handling errors and setting HTTP status codes"""

    def on_operation(self):
        """Hook for operation execution"""
        yield  # Let the operation execute
        # Process errors after execution
        self.process_errors()

    def process_errors(self) -> None:
        """Process errors and set appropriate HTTP status codes"""
        execution_context = self.execution_context
        errors = getattr(execution_context, 'pre_execution_errors', None)

        if not execution_context or not errors:
            return

        _process_errors_impl(
            errors=errors,
            execution_context=execution_context
        )


def _process_errors_impl(
    errors: List[GraphQLError],
    execution_context: Optional[ExecutionContext] = None
) -> None:
    """
    Process GraphQL errors and set appropriate HTTP status codes.

    This handler translates domain exceptions to proper HTTP semantics:
    - Authentication/Authorization errors: 401/403
    - Not found errors: 404
    - Bad request errors: 400
    - Rate limiting errors: 429
    - Server errors: 500/503
    - Business logic errors: 200 (kept as GraphQL errors)

    All errors include structured extensions for client-side handling.
    """
    if not execution_context:
        return

    # Determine the most appropriate HTTP status code
    highest_priority_code = 200
    has_auth_error = False
    has_server_error = False

    for error in errors:
        original_error = error.original_error

        # Initialize extensions if not present
        if error.extensions is None:
            error.extensions = {}

        # Handle our custom exceptions
        if isinstance(original_error, GenericException):
            error_code = original_error.code

            # Add structured error information
            error.extensions.update({
                "code": error_code,
                "exception_type": type(original_error).__name__,
            })

            # Prioritize certain error types for HTTP status code
            # Auth errors take highest priority
            if isinstance(original_error, (UnauthorizedException, ForbiddenException)):
                highest_priority_code = error_code
                has_auth_error = True
                logger.warning(f"Authentication/Authorization error: {str(original_error)}")

            # Server errors take second priority
            elif isinstance(original_error, (InternalServerException, ServiceUnavailableException)):
                if not has_auth_error:
                    highest_priority_code = error_code
                has_server_error = True
                logger.error(f"Server error: {str(original_error)}", exc_info=original_error)

            # Rate limiting is also high priority
            elif isinstance(original_error, RateLimitExceededException):
                if not has_auth_error and not has_server_error:
                    highest_priority_code = error_code
                logger.warning(f"Rate limit exceeded: {str(original_error)}")

            # Client errors (400, 404) - use if no higher priority errors
            elif isinstance(original_error, (BadRequestException, NotFoundException)):
                if highest_priority_code == 200:
                    highest_priority_code = error_code

            # Log the error appropriately
            if error_code >= 500:
                logger.error(f"Error in GraphQL execution: {str(original_error)}", exc_info=original_error)
            elif error_code >= 400:
                logger.warning(f"Client error in GraphQL execution: {str(original_error)}")

        else:
            # Handle unexpected errors (not our custom exceptions)
            if original_error:
                error.extensions["exception_type"] = type(original_error).__name__
                logger.error(f"Unexpected error in GraphQL execution: {str(original_error)}", exc_info=original_error)
                if not has_auth_error and highest_priority_code < 500:
                    highest_priority_code = 500
            else:
                # GraphQL validation errors, etc.
                error.extensions["exception_type"] = "GraphQLError"

    # Set the HTTP status code on the response
    if highest_priority_code != 200:
        execution_context.context["response"].status_code = highest_priority_code
