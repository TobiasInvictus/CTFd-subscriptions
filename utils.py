from collections import namedtuple
from sqlalchemy.sql import and_
from CTFd.cache import cache
from CTFd.models import Challenges
from CTFd.schemas.tags import TagSchema
from CTFd.utils.helpers.models import build_model_filters


Challenge = namedtuple(
    "Challenge", ["id", "type", "name", "value", "category", "tags", "requirements"]
)

@cache.memoize(timeout=60)
def get_all_challenges(admin=False, field=None, q=None, sub=None, **query_args):
    filters = build_model_filters(model=Challenges, query=q, field=field)
    chal_q = Challenges.query

    if sub == "freemium":
        chal_q = chal_q.filter(
            and_(Challenges.subscription_required == "freemium", Challenges.state != "locked")
        )
    elif sub == "premium":
        chal_q = chal_q.filter(
            and_((Challenges.subscription_required == "freemium") | (Challenges.subscription_required == "premium"), Challenges.state != "locked")
        )
    elif sub == "bleeding-edge":
        chal_q = chal_q.filter(
            and_(Challenges.state != "hidden", Challenges.state != "locked")
        )

    chal_q = (
        chal_q.filter_by(**query_args)
        .filter(*filters)
        .order_by(Challenges.value, Challenges.id)
    )

    tag_schema = TagSchema(view="user", many=True)

    results = []
    for c in chal_q:
        ct = Challenge(
            id=c.id,
            type=c.type,
            name=c.name,
            value=c.value,
            category=c.category,
            requirements=c.requirements,
            tags=tag_schema.dump(c.tags).data,
        )
        results.append(ct)
    return results
