from __future__ import annotations


import argparse
import json

from src.schemas.ingest import IngestRequest
from src.schemas.query import QueryRequest
from src.services.ingest_service import IngestService
from src.services.query_service import QueryService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='docquery')
    subparsers = parser.add_subparsers(dest='command', required=True)

    ingest_parser = subparsers.add_parser('ingest', help='Ingest one or more documents')
    ingest_parser.add_argument('paths', nargs='+', help='Paths to documents')

    query_parser = subparsers.add_parser('query', help='Query indexed documents')
    query_parser.add_argument('question', help='Question to ask')
    query_parser.add_argument('--top-k', type=int, default=5)
    query_parser.add_argument('--min-score', type=float, default=None)
    query_parser.add_argument('--no-snippets', action='store_true')

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == 'ingest':
        service = IngestService()
        response = service.ingest(IngestRequest(paths=args.paths))
        print(json.dumps(response.model_dump(mode='json'), indent=2))
    
    elif args.command == 'query':
        service = QueryService()
        response = service.query(
            QueryRequest(
                question=args.question,
                top_k=args.top_k,
                min_score=args.min_score,
                return_snippets=not args.no_snippets
            )
        )

        print(json.dumps(response.model_dump(mode='json'), indent=2))


if __name__ == '__main__':
    main()