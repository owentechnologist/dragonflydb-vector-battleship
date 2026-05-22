import os
import struct
from connect_to_datastore import connect_to_datastore
from redis.commands.search.field import TagField, NumericField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

# Set DRAGONFLY_HOST / DRAGONFLY_PORT / DRAGONFLY_PASSWORD env vars to override defaults.
TABLE_CONFIGS = {
    'vb.battleship': {'prefix': 'ship:battleship:', 'index_name': 'idx:battleship', 'dim': 105},
    'vb.battle_v21': {'prefix': 'ship:battle_v21:', 'index_name': 'idx:battle_v21', 'dim': 21},
    'vb.battle_v11': {'prefix': 'ship:battle_v11:', 'index_name': 'idx:battle_v11', 'dim': 11},
}


'''
# now imported from connect_to_datastore.py
_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=os.getenv('DRAGONFLY_HOST', 'localhost'),
            port=int(os.getenv('DRAGONFLY_PORT', 6379)),
            password=os.getenv('DRAGONFLY_PASSWORD') or None,
            decode_responses=False,
        )
        ensure_indices(_redis_client)
    return _redis_client
'''

def get_table_config(table_name):
    return TABLE_CONFIGS.get(table_name, TABLE_CONFIGS['vb.battleship'])

# creates all 3 indexes (one for each possible vector dimension type)
def ensure_indices():
    connection=connect_to_datastore()
    #print(f"Ensuring search indexes exist... in {connection}")
    for config in TABLE_CONFIGS.values():
        try:
            connection.ft(config['index_name']).create_index(
                [
                    TagField('battleship_class'),
                    NumericField('quadrant'),
                    NumericField('anchorpoint'),
                    VectorField('embedding', 'FLAT', {
                        'TYPE': 'FLOAT32',
                        'DIM': config['dim'],
                        'DISTANCE_METRIC': 'L2',
                    }),
                ],
                definition=IndexDefinition(
                    prefix=[config['prefix']],
                    index_type=IndexType.HASH,
                ),
            )
            print(f"Created index {config['index_name']}")
        except Exception:
            pass  # Index already exists


def close_pool():
    pass


def _s(v):
    return v.decode() if isinstance(v, bytes) else str(v) if v is not None else None


def vector_search(table_name, quadrant, vector, threshold):
    """Return ships in quadrant whose L2 similarity meets threshold, sorted best-first."""
    connection = connect_to_datastore()
    config = get_table_config(table_name)
    vec_bytes = struct.pack(f'{len(vector)}f', *[float(v) for v in vector])
    q = (
        Query(f'@quadrant:[{quadrant} {quadrant}]=>[KNN 10 @embedding $vec AS dist]')
        .sort_by('dist')
        .return_fields('battleship_class', 'anchorpoint', 'dist')
        .paging(0, 10)
        .dialect(2)
    )
    results = connection.ft(config['index_name']).search(q, query_params={'vec': vec_bytes})
    matched = []
    for doc in results.docs:
        dist = float(_s(doc.dist))
        match_pct = round((1 / (1 + dist)) * 100, 2)
        if match_pct >= threshold:
            uid = _s(doc.id).rsplit(':', 1)[1]
            matched.append({
                'uuid': uid,
                'ship_class': _s(doc.battleship_class),
                'anchorpoint': int(_s(doc.anchorpoint)),
                'match_percentage': match_pct,
            })
    return matched


def destroy_ship(table_name, ship_uuid):
    connection = connect_to_datastore()
    config = get_table_config(table_name)
    connection.delete(f"{config['prefix']}{ship_uuid}")


def get_max_quadrants(table_name):
    connection = connect_to_datastore()
    config = get_table_config(table_name)
    val = connection.get(f"meta:{config['index_name']}:max_quadrant")
    return int(val) if val else 4
