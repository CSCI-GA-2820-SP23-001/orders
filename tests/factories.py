# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
from datetime import date
import random
import factory
from factory.fuzzy import FuzzyDate
from service.models import Order, Item


class OrderFactory(factory.Factory):
    """Creates fake Orders"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Order

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    street = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")
    postal_code = factory.Faker("postalcode")
    shipping_price = round(random.uniform(1.00, 100.00), 2)
    date_created = FuzzyDate(date(2008, 1, 1))
    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @factory.post_generation
    def items(self, create, extracted, **kwargs):   # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(factory.Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Item

    id = factory.Sequence(lambda n: n)
    sku = factory.Sequence(lambda n: n)
    item_price = round(random.uniform(1.00, 100.00), 2)
    order_id = None
    order = factory.SubFactory(OrderFactory)
