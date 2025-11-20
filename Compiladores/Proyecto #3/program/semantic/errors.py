class SemanticError(Exception):
    pass

def at(ctx, msg: str) -> 'SemanticError':
    token = getattr(ctx, 'start', None)
    if token is not None:
        return SemanticError(f"[Semantic] line {token.line}:{token.column} {msg}")
    return SemanticError(f"[Semantic] {msg}")
