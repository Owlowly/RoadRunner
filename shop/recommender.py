from collections import defaultdict, Counter
from django.db.models import Count
from .models import Product, Interaction

class Recommender:
    def __init__(self):
        self.product_interactions = defaultdict(lambda: defaultdict(int))

    def get_product_key(self, product_id):
        return f'product:{product_id}:purchased_with'

    def products_bought(self, products):
        product_ids = [p['product'].id for p in products]
        for i, product_id in enumerate(product_ids):
            for with_id in product_ids[i + 1:]:
                product_key = self.get_product_key(product_id)
                self.product_interactions[product_key][with_id] += 1
        self.save_interactions_to_db()

    def save_interactions_to_db(self):
        for product_key, interactions in self.product_interactions.items():
            product_id = int(product_key.split(":")[1])
            for with_id, score in interactions.items():
                interaction, _ = Interaction.objects.get_or_create(product_id=product_id,
                                                                   with_product_id=with_id)
                existing_score = interaction.score
                interaction.score = existing_score + score
                interaction.save()

    def suggest_products_for(self, products, max_results=3):
        product_ids = [p.id for p in products]
        # If only one product is provided
        if len(products) == 1:
            product_id = product_ids[0]
            suggestions = Interaction.objects.filter(product_id=product_id).order_by('-score')[:max_results]
            suggested_product_ids = [suggestion.with_product_id for suggestion in suggestions]
            suggested_products = Product.objects.filter(id__in=suggested_product_ids)
            return suggested_products

        # If multiple products are provided
        else:
            # Combine scores of all products
            interactions = Interaction.objects.filter(
                product_id__in=product_ids).values('with_product_id').annotate(score_sum=Count('score'))
            suggestion_counter = Counter(
                {interaction['with_product_id']: interaction['score_sum'] for interaction in interactions})
            suggested_product_ids = [product_id for product_id, _ in suggestion_counter.most_common(max_results)]
            suggested_products = Product.objects.filter(id__in=suggested_product_ids)
            return suggested_products

    def clear_purchases(self):
        self.product_interactions = defaultdict(lambda: defaultdict(int))
