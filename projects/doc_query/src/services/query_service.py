from src.schemas.query import QueryRequest, QueryResponse


class QueryService:
    def query(self, request: QueryRequest) -> QueryResponse:
        raise NotImplementedError('QueryService.query is not yet implemented')