from src.models.prices import PriceOrm
from src.schemas.prices import PriceRead

class PriceDataMapper:
    schema = PriceRead
    db_model = PriceOrm

    @classmethod
    def map_to_domain_entity_pyd(cls, model: PriceOrm) -> PriceRead:
        return cls.schema.model_validate(model)
