from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.company import CompanyService
from app.utils.db_util import get_db
import structlog
from app.schemas.base import AUTH_ERROR, ResponseModel

logger = structlog.get_logger()

class CompanyContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts API key from request headers,
    validates it against the database, and sets company context
    in request state.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Check if path requires API key authentication
        # For multi-tenancy RAG endpoints like "/docs/reviews/query"
        if not self._requires_api_key(request.url.path):
            return await call_next(request)
           
        # Extract API key from headers
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            logger.warning("missing_api_key", path=request.url.path)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=ResponseModel(
                    code=AUTH_ERROR,
                    message="Missing API key",
                    data=None
                ).model_dump()
            )
            
        # Get database session
        try:
            # Need to get an async session from the dependency
            db_gen = get_db()
            db: AsyncSession = await db_gen.__anext__()
            
            # Initialize service and validate API key
            company = await CompanyService.get_company_by_api_key(db, api_key)
            
            if not company:
                logger.warning("invalid_api_key", api_key=api_key, path=request.url.path)
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=ResponseModel(
                        code=AUTH_ERROR,
                        message="Invalid API key",
                        data=None
                    ).model_dump()
                )
                
            if not company.is_active:
                logger.warning("inactive_company", company_uuid=company.company_uuid, path=request.url.path)
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ResponseModel(
                        code=AUTH_ERROR,
                        message="Company is inactive",
                        data=None
                    ).model_dump()
                )
                
            # Set company context in request state
            request.state.company = company
            request.state.company_uuid = company.company_uuid
            
            # Call next middleware/route handler
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "api_key_middleware_error",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponseModel(
                    code=AUTH_ERROR,
                    message="An error happened during authentication",
                    data=None
                ).model_dump()
            )
        finally:
            # Clean up database session
            if 'db_gen' in locals() and 'db' in locals():
                try:
                    await db.close()
                except Exception:
                    pass
                    
    def _requires_api_key(self, path: str) -> bool:
        """Check if the current path requires API key authentication."""
        # Skip OpenAPI documentation paths
        if path.startswith("/api/docs") or path.startswith("/api/redoc") or path.endswith("/openapi.json"):
            return False
            
        # Add paths that require API key auth here
        auth_paths = [
            "/api/v1/companies/info",
        ]
        
        # Check if path matches any of the auth paths or starts with them
        for auth_path in auth_paths:
            if path == auth_path or path.startswith(f"{auth_path}/"):
                return True
                
        return False
